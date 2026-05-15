# Bun 打包器（Bundler）源码架构分析

> 深入分析 Bun 内置打包器的实现原理，包括解析、链接、Tree Shaking、代码分割、CSS 处理等核心机制。

---

## 一、打包器架构概览

Bun 的打包器是一个**从零实现的 Zig 原生打包器**，API 设计深受 esbuild 启发，但实现完全独立。它与运行时的解析器、转译器深度集成，共享底层基础设施。

```
┌─────────────────────────────────────────────────────────────┐
│                    Bun Bundler 流程                         │
│                                                             │
│  输入: entrypoints: ['./src/index.tsx']                     │
│                                                             │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. 扫描阶段 (Scan)                                   │   │
│  │    - 解析入口文件                                    │   │
│  │    - 递归发现所有导入                                │   │
│  │    - 构建模块图                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 2. 解析阶段 (Parse)                                  │   │
│  │    - Lexer 分词                                     │   │
│  │    - Parser 生成 AST                                │   │
│  │    - 转译 TS/JSX → JS                               │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 3. 链接阶段 (Link)                                   │   │
│  │    - 符号解析                                       │   │
│  │    - Tree Shaking (DCE)                             │   │
│  │    - 作用域提升                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 4. 代码生成 (CodeGen)                                │   │
│  │    - 分块 (Chunking)                                │   │
│  │    - 代码分割 (Splitting)                           │   │
│  │    - Minify/压缩                                    │   │
│  └─────────────────────────────────────────────────────┘   │
│       │                                                     │
│       ▼                                                     │
│  输出: ./dist/                                              │
│        ├── index.js                                         │
│        ├── chunk-*.js                                       │
│        └── index.css                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、扫描阶段（Scan Phase）

### 2.1 模块发现

打包器从入口文件开始，递归发现所有依赖：

```zig
// src/bundler/bundle_v2.zig
pub fn scan(
    self: *BundleV2,
    entrypoints: []const []const u8,
) !ModuleGraph {
    var graph = ModuleGraph.init(self.allocator);
    
    // 并行扫描所有入口
    var wg = WaitGroup.init();
    for (entrypoints) |entry| {
        wg.start();
        try self.scanFile(entry, &graph, &wg);
    }
    wg.wait();
    
    return graph;
}
```

### 2.2 解析器集成

扫描阶段复用 Bun 运行时的模块解析器：

```
扫描阶段
    │
    ├──→ 相对路径导入 → src/resolver/resolver.zig
    │
    ├──→ node_modules 导入 → src/resolver/package_json.zig
    │
    ├──→ 内置模块 → src/resolve_builtins/
    │
    └──→ 外部模块 → 标记为 external
```

---

## 三、解析阶段（Parse Phase）

### 3.1 Lexer 实现

Bun 的 Lexer 使用 Zig 实现，针对性能优化：

```zig
// src/js_parser/js_lexer.zig
pub const Lexer = struct {
    source: []const u8,
    current: usize,
    
    // SIMD 加速的标识符识别
    pub fn nextToken(self: *Lexer) Token {
        // 使用 SIMD 指令批量处理空白字符
        self.skipWhitespaceSIMD();
        
        // 快速路径：单字符 token
        const ch = self.source[self.current];
        switch (ch) {
            '{' => { self.current += 1; return .brace_open; },
            '}' => { self.current += 1; return .brace_close; },
            // ...
            else => return self.parseIdentifierOrKeyword(),
        }
    }
};
```

### 3.2 Parser 架构

Parser 生成 Bun 的自定义 AST 格式：

```zig
// src/ast/ast.zig
pub const Expr = union(enum) {
    e_array: EArray,
    e_binary: EBinary,
    e_call: ECall,
    e_function: EFunction,
    e_import: EImport,
    e_class: EClass,
    // ...
};

pub const Stmt = union(enum) {
    s_block: SBlock,
    s_expr: SExpr,
    s_return: SReturn,
    s_import: SImport,
    s_export: SExport,
    // ...
};
```

### 3.3 TypeScript / JSX 转译

Parser 在解析的同时完成转译，避免额外的 AST pass：

```
输入: .tsx 文件
       │
       ▼
┌─────────────────┐
│ Lexer           │
│ - JSX 语法识别  │
│ - Type 注解识别 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Parser          │
│ - 生成 AST      │
│ - 丢弃 Type 节点│
│ - 转换 JSX → JS │
└────────┬────────┘
         │
         ▼
输出: 标准 JS AST（无需额外转译步骤）
```

---

## 四、链接阶段（Link Phase）

### 4.1 符号解析

链接器将跨模块的符号引用解析为实际定义：

```zig
// src/bundler/LinkerContext.zig
pub const LinkerContext = struct {
    pub fn link(self: *LinkerContext, graph: *ModuleGraph) !void {
        // 1. 收集所有导出符号
        for (graph.modules) |*module| {
            self.collectExports(module);
        }
        
        // 2. 解析导入符号
        for (graph.modules) |*module| {
            self.resolveImports(module);
        }
        
        // 3. 标记可达代码（用于 Tree Shaking）
        self.markReachableCode(graph);
    }
};
```

### 4.2 Tree Shaking（死代码消除）

Bun 的 Tree Shaking 基于 **Part 图** 遍历：

```
模块文件
    │
    ├──→ 顶层语句 1 (Part A)
    │       ├── 导出符号: foo
    │       └── 引用符号: bar
    │
    ├──→ 顶层语句 2 (Part B)
    │       ├── 导出符号: baz
    │       └── 引用符号: qux
    │
    └──→ 顶层语句 3 (Part C)
            └── 无导出（可能为死代码）

入口点导入 foo
    │
    ▼
Part A 被标记为 "live"
    │
    └──→ Part A 引用 bar
              │
              └──→ 查找 bar 定义
                        │
                        └──→ 标记包含 bar 的 Part 为 "live"

未被标记的 Part C → 死代码 → 移除
```

**核心源码文件：**

| 文件 | 职责 |
|------|------|
| `src/bundler/computeCrossChunkDependencies.zig` | 计算跨块依赖，确定活代码边界 |
| `src/bundler/postProcessJSChunk.zig` | 标记死代码符号 |
| `src/bundler/renameSymbolsInChunk.zig` | DCE 完成后重命名标识符（minify） |

### 4.3 作用域提升（Scope Hoisting）

Bun 将 ESM 模块的作用域提升到 bundle 级别，减少运行时开销：

```javascript
// 原始 ESM 模块
// module-a.js
export const foo = 1;

// module-b.js
import { foo } from './module-a';
console.log(foo);

// 传统打包（包裹函数）
var modules = {
  'module-a': function(exports) { exports.foo = 1; },
  'module-b': function(exports) { console.log(modules['module-a'].foo); }
};

// Bun 作用域提升后
const foo = 1;  // 直接内联
console.log(foo);
```

---

## 五、代码生成阶段

### 5.1 分块策略

Bun 根据配置将代码分割为多个 chunk：

```javascript
// Bun.build 配置
await Bun.build({
  entrypoints: ['./src/index.ts', './src/admin.ts'],
  outdir: './dist',
  splitting: true,  // 启用代码分割
});

// 输出：
// dist/index.js      - 入口 1
// dist/admin.js      - 入口 2
// dist/chunk-shared.js - 共享代码
```

### 5.2 Minify 实现

Bun 的 minifier 在链接阶段之后运行：

```zig
// Minify 配置
minify: {
  syntax: true,      // 移除不可达语句、死分支
  identifiers: true, // 重命名变量（mangling）
  whitespace: true,  // 移除空白字符
}
```

**Minify 流程：**

```
AST（链接后）
    │
    ├──→ Syntax Minify
    │       - 常量折叠: 1 + 2 → 3
    │       - 死分支移除: if (false) { ... }
    │       - 空语句移除
    │
    ├──→ Identifier Minify
    │       - 短变量名: myVariable → a
    │       - 保留导出符号（如果构建库）
    │
    └──→ Whitespace Minify
            - 移除所有非必要空白
            - 生成 sourcemap
```

---

## 六、CSS 处理

### 6.1 CSS 解析器

Bun 内置 CSS 解析器，支持 CSS Modules：

```
src/css/
├── css.zig           # CSS 解析核心
├── css_derive/       # CSS 派生宏
└── css_jsc/          # JSC 绑定
```

### 6.2 CSS 打包流程

```
@import "./styles.css"
       │
       ▼
┌─────────────────┐
│ CSS 解析器       │
│ - 解析 @import   │
│ - 解析 @url()    │
│ - 提取 class 名  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ CSS Modules      │
│ - 生成唯一类名   │
│ - 导出 JS 映射   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 合并 & Minify   │
│ - 去重规则      │
│ - 压缩空白      │
└─────────────────┘
```

---

## 七、插件系统

### 7.1 插件 API

Bun 提供与 esbuild 兼容的插件 API：

```typescript
// 插件示例
const myPlugin: BunPlugin = {
  name: 'my-plugin',
  setup(build) {
    // 拦截特定路径的解析
    build.onResolve({ filter: /^\.svg$/ }, (args) => {
      return { path: args.path, namespace: 'svg' };
    });
    
    // 提供加载逻辑
    build.onLoad({ filter: /.*/, namespace: 'svg' }, (args) => {
      return {
        contents: `export default ${JSON.stringify(readFile(args.path))}`,
        loader: 'js',
      };
    });
  },
};

await Bun.build({
  entrypoints: ['./src/index.ts'],
  plugins: [myPlugin],
});
```

### 7.2 插件执行模型

```
主进程 (Zig)
    │
    ├──→ 发现需要插件处理的文件
    │
    └──→ 启动轻量级 Bun 子进程
            │
            ├──→ 加载插件代码
            ├──→ 执行 onResolve/onLoad
            └──→ 返回结果给主进程

优势：
- 插件在独立进程中运行，崩溃不影响主进程
- Bun 进程启动快，插件执行开销低
- 插件可以使用完整的 Bun API
```

---

## 八、与 esbuild 的架构对比

| 维度 | esbuild | Bun Bundler |
|------|---------|-------------|
| **实现语言** | Go | Zig |
| **解析器** | 自研 | 自研（与运行时共享） |
| **Tree Shaking** | 基于 Part 图 | 基于 Part 图（类似设计） |
| **作用域提升** | 支持 | 支持 |
| **代码分割** | 支持 | 支持 |
| **CSS 处理** | 内置 | 内置 |
| **插件系统** | onResolve/onLoad | 兼容 esbuild API |
| **Sourcemap** | 支持 | 支持 |
| **性能** | 极快 | 更快（1.75x esbuild） |

---

## 九、核心源码文件

| 功能 | 核心文件 |
|------|---------|
| 打包器主流程 | `src/bundler/bundle_v2.zig` |
| 链接上下文 | `src/bundler/LinkerContext.zig` |
| 跨块依赖计算 | `src/bundler/computeCrossChunkDependencies.zig` |
| JS 块后处理 | `src/bundler/postProcessJSChunk.zig` |
| 符号重命名 | `src/bundler/renameSymbolsInChunk.zig` |
| JS 解析器 | `src/js_parser/js_parser.zig` |
| JS 打印器 | `src/js_printer/js_printer.zig` |
| 转译器 | `src/transpiler/transpiler.zig` |
| CSS 处理 | `src/css/css.zig` |
| 模块解析 | `src/resolver/resolver.zig` |
| Sourcemap | `src/sourcemap/sourcemap.zig` |

---

## 十、参考资源

- [Bun Bundler Docs](https://bun.sh/docs/bundler)
- [Bun Bundler Blog Post](https://bun.sh/blog/bun-bundler)
- [Bun vs esbuild](https://bun.sh/docs/bundler/esbuild)
- [esbuild Architecture Docs](https://github.com/evanw/esbuild/blob/main/docs/architecture.md)
