# Bun JavaScript 运行时架构分析

> 深入分析 Bun 的 JavaScript 运行时实现，包括 JSC 集成、模块系统、事件循环、Node.js 兼容层等核心机制。

---

## 一、运行时核心架构

Bun 的运行时基于 **WebKit JavaScriptCore（JSC）** 引擎，通过 Zig 编写的绑定层与原生代码交互。整个运行时的核心集成点是 `Zig::GlobalObject`，它继承自 JSC 的 `JSGlobalObject`。

```
┌─────────────────────────────────────────────┐
│           JavaScript 代码层                  │
│  ┌─────────┐ ┌─────────┐ ┌───────────────┐ │
│  │ 用户代码 │ │内置模块 │ │ Web APIs      │ │
│  │         │ │node:fs  │ │ fetch, WS     │ │
│  └────┬────┘ └────┬────┘ └───────┬───────┘ │
└───────┼───────────┼──────────────┼─────────┘
        │           │              │
        └───────────┴──────────────┘
                    │
        ┌───────────▼───────────┐
        │  Zig::GlobalObject    │  ← 中央集成点
        │  extends JSGlobalObject│
        └───────────┬───────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼───┐    ┌─────▼─────┐   ┌────▼────┐
│ JSC   │    │  Bun API  │   │ Node.js │
│ 引擎  │    │  绑定层   │   │ 兼容层  │
│       │    │ (Zig)     │   │ (Zig)   │
└───────┘    └───────────┘   └─────────┘
```

---

## 二、JavaScriptCore 集成

### 2.1 绑定层设计

Bun 使用 **C++ + Zig 混合绑定** 的方式与 JSC 交互：

```
JavaScript 对象 ←→ C++ 绑定层 ←→ Zig 运行时
     │                │              │
     │         ┌──────┴──────┐       │
     │         │  ZigGlobal  │       │
     │         │  Object     │       │
     │         └──────┬──────┘       │
     │                │              │
  JSC API        ZIG_EXPORT      Zig 函数
```

**核心绑定文件：**

| 文件 | 职责 |
|------|------|
| `src/bun.js/bindings/ZigGlobalObject.h` | 全局对象头文件，定义 `Zig::GlobalObject` 类 |
| `src/bun.js/bindings/ZigGlobalObject.cpp` | 全局对象实现，初始化 JSC 环境 |
| `src/bun.js/bindings/bindings.cpp` | 通用绑定工具函数 |
| `src/bun.js/bindings/bindings.zig` | Zig 侧的绑定接口 |
| `src/bun.js/bindings/BunString.cpp` | 字符串在 JSC 和 Zig 间的桥接 |

### 2.2 ZIG_EXPORT 机制

Bun 使用 `[[ZIG_EXPORT]]` 属性标记需要从 Zig 调用的 C++ 函数：

```cpp
// C++ 侧（src/bun.js/bindings/BunString.cpp）
extern "C" [[ZIG_EXPORT(nothrow)]]
BunString BunString__fromJS(
    JSC::JSGlobalObject* globalObject,
    JSC::EncodedJSValue encodedValue,
    BunString* bunString
) {
    JSC::JSValue value = JSC::JSValue::decode(encodedValue);
    *bunString = Bun::toString(globalObject, value);
    return *bunString;
}
```

```zig
// Zig 侧调用
const bunString = BunString__fromJS(globalObject, encodedValue, &result);
```

### 2.3 BunString 字符串桥接

字符串是 JS ↔ 原生交互最频繁的数据类型。Bun 实现了高效的字符串桥接：

```cpp
// BunString 使用 tagged union 表示不同来源的字符串
struct BunString {
    enum Tag : uint8_t {
        Dead = 0,           // 无效字符串
        WTFStringImpl,      // JSC/WTF 字符串
        ZigString,          // Zig 字符串
        StaticZigString,    // 静态 Zig 字符串
    } tag;
    
    union {
        WTF::StringImpl* wtf;   // JSC 内部字符串
        ZigString zig;           // Zig 字符串切片
    };
};
```

**优化点：**
- 尽可能使用 **zero-copy** 传递字符串引用
- 使用 `simdutf` 库进行快速的 UTF-8 验证和转换
- 原子字符串（AtomString）缓存常用字符串

---

## 三、模块系统与加载

### 3.1 模块解析流程

```
import "./foo.ts"
       │
       ▼
┌──────────────┐
│ 模块解析器    │  ← src/resolver/resolver.zig
│ (Resolver)   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 路径解析      │
│ - 相对路径    │
│ - node_modules│
│ - 内置模块    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 文件加载      │  ← src/module_loader.zig
│ - .ts → 转译  │
│ - .js → 直接  │
│ - .json → 解析│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ JSC 编译执行  │
│ - 生成字节码  │
│ - 缓存编译结果│
└──────────────┘
```

### 3.2 内置模块实现

Bun 的内置模块（如 `node:fs`、`bun:ffi`）使用 **TypeScript 编写源码 + Zig 实现核心逻辑** 的混合模式：

```
src/js/builtins/
├── BunBuiltinNames.h          # 内置名称定义
├── BunBuiltinNames.cpp        # 名称实现
├── node/                      # Node.js 兼容模块
│   ├── fs.ts                  # fs 模块的 TS 接口
│   ├── path.ts                # path 模块
│   └── ...
└── bun/                       # Bun 专属模块
    ├── ffi.ts                 # FFI 接口
    ├── sqlite.ts              # SQLite 接口
    └── ...
```

**代码生成流程：**

```
TypeScript 源码 (.ts)
       │
       ▼
┌──────────────┐
│ Bun Bundler  │  ← 打包内置模块
│ (自举)       │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ C++ 头文件   │  ← 生成 JSC 类绑定
│ 生成器       │
└──────┬───────┘
       │
       ▼
编译进 bun 可执行文件
```

### 3.3 ESM / CJS 双模块支持

Bun 的解析器同时支持 ESM 和 CommonJS 语法，在 AST 层面统一处理：

```zig
// src/js_parser/js_parser.zig
// 解析器将 ESM 和 CJS 都转换为统一的内部表示

// ESM: import { foo } from "bar"
//  → 标记为 ESM 导入符号

// CJS: const foo = require("bar")
//  → 同样标记为导入符号，但附加 CJS 标记

// 链接阶段统一处理两种模块格式
```

---

## 四、事件循环

### 4.1 事件循环架构

Bun 的事件循环基于 **io_uring**（Linux）和 **kqueue**（macOS/BSD），而非传统的 libuv：

```
┌─────────────────────────────────────────┐
│           Bun Event Loop                │
│                                         │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 微任务   │◄───│ Promise/queue   │    │
│  │ 队列    │    │ Microtask       │    │
│  └────┬────┘    └─────────────────┘    │
│       │                                 │
│       ▼                                 │
│  ┌─────────┐    ┌─────────────────┐    │
│  │ 宏任务   │◄───│ Timers/IO/      │    │
│  │ 队列    │    │ Network Events  │    │
│  └────┬────┘    └─────────────────┘    │
│       │                                 │
│       ▼                                 │
│  ┌─────────────────────────────────┐   │
│  │     io_uring / kqueue           │   │
│  │  (异步 I/O 多路复用)             │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

### 4.2 io_uring 优势

相比 libuv 的线程池 + epoll，io_uring 提供了：

| 特性 | libuv (Node.js) | io_uring (Bun) |
|------|----------------|----------------|
| 系统调用次数 | 每次 I/O 至少 2 次 | 批量提交，大幅减少 |
| 用户态/内核态切换 | 频繁 | 最小化 |
| 异步文件 I/O | 线程池模拟 | 真正的内核异步 |
| 缓冲区管理 | 用户态分配 | 支持 registered buffers |

**关键代码：**

```zig
// src/io/io.zig - io_uring 封装
pub const IO = struct {
    ring: io_uring,
    
    pub fn init(entries: u13) !IO {
        var ring: io_uring = undefined;
        try ring.init(entries, 0);
        return IO{ .ring = ring };
    }
    
    // 批量提交 I/O 请求
    pub fn flush(self: *IO) !void {
        _ = try self.ring.submit();
    }
};
```

---

## 五、Node.js 兼容层

### 5.1 兼容策略

Bun 的 Node.js 兼容层采用 **重新实现 + 代理** 的策略：

```
用户代码 require("fs")
       │
       ▼
┌──────────────┐
│ 模块加载器    │
│ 识别为内置模块│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Node.js 兼容  │
│ 层 (Zig)     │
│              │
│ ┌──────────┐ │
│ │ 优先使用  │ │ ← Bun 原生实现（更快）
│ │ 原生 API  │ │
│ └──────────┘ │
│       │      │
│ ┌─────▼─────┐│
│ │ 回退到    ││ ← 兼容边缘情况
│ │ Node 行为 ││
│ └───────────┘│
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 系统调用层    │
│ src/sys.zig  │
└──────────────┘
```

### 5.2 核心模块映射

| Node.js 模块 | Bun 实现位置 | 实现方式 |
|-------------|-------------|---------|
| `fs` | `src/bun.js/node/node_fs.zig` | Zig 原生实现 |
| `path` | `src/bun.js/node/` | Zig 原生实现 |
| `crypto` | `src/bun.js/api/crypto.zig` | Zig + BoringSSL |
| `http` | `src/bun.js/api/server.zig` | 原生 HTTP 栈 |
| `net` | `src/bun.js/node/` | Zig 实现 |
| `stream` | `src/bun.js/webcore/streams.zig` | Web Streams 兼容 |
| `buffer` | `src/bun.js/node/types.zig` | Zig 实现 |

### 5.3 N-API 兼容

Bun 支持 Node.js 的 N-API（Native Addon API），允许使用 C/C++ 编写的原生模块无需重新编译即可运行：

```
原生模块 (.node)
       │
       ▼
┌──────────────┐
│ N-API 兼容层  │  ← src/bun.js/node/napi.zig
│              │
│ - 函数导出    │
│ - 类型转换    │
│ - 内存管理    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ JSC 对象封装  │
└──────────────┘
```

---

## 六、内存管理

### 6.1 多语言内存模型

Bun 涉及三种内存管理模型：

| 语言 | 内存模型 | 管理方式 |
|------|---------|---------|
| **JavaScript** | GC | JSC 的垃圾回收器（标记-清除/整理） |
| **Zig** | 手动 | 显式分配/释放，使用 Arena Allocator |
| **C++** | RAII + 智能指针 | JSC/WTF 的引用计数 |

### 6.2 跨语言对象生命周期

```
JS 对象 (GC 管理)
     │
     │ 引用
     ▼
┌─────────┐
│ C++ 包装 │  ← RefPtr 引用计数
│ 对象     │
└────┬────┘
     │
     │ 指针
     ▼
┌─────────┐
│ Zig 数据 │  ← 手动/Allocator 管理
│ 结构     │
└─────────┘
```

**关键规则：**
- JS 对象被 GC 回收时，触发 C++ 析构函数
- C++ 析构函数释放对 Zig 数据的引用
- Zig 侧使用 `defer` 或 Arena 确保内存释放

### 6.3 自定义分配器

Bun 使用多种专用分配器优化内存使用：

```zig
// src/allocators/bun_alloc/
pub const BunAllocator = struct {
    // 小对象分配器 - 针对频繁分配的小对象优化
    small_object: SmallObjectAllocator,
    
    // 大对象分配器 - 直接委托给系统 malloc
    large_object: std.heap.c_allocator,
    
    // Arena 分配器 - 用于临时/批量分配
    arena: std.heap.ArenaAllocator,
};
```

---

## 七、关键源码文件速查

| 功能 | 核心文件 |
|------|---------|
| 运行时入口 | `src/bun.zig` |
| CLI 解析 | `src/cli.zig` |
| JSC 全局对象 | `src/bun.js/bindings/ZigGlobalObject.cpp` |
| 模块加载 | `src/bun.js/module_loader.zig` |
| 事件循环 | `src/bun.js/event_loop.zig` |
| HTTP 服务器 | `src/bun.js/api/server.zig` |
| Fetch API | `src/bun.js/webcore/fetch.zig` |
| 文件系统 | `src/bun.js/node/node_fs.zig` |
| 加密 | `src/bun.js/api/crypto.zig` |
| 系统调用 | `src/sys/sys.zig` |
| I/O 抽象 | `src/io/io.zig` |

---

## 八、参考资源

- [Bun Runtime Docs](https://bun.sh/docs/runtime)
- [JSC API Reference](https://developer.apple.com/documentation/javascriptcore)
- [Bun Node.js Compatibility](https://bun.sh/docs/runtime/nodejs-compat)
- [io_uring 介绍](https://kernel.dk/io_uring.pdf)
