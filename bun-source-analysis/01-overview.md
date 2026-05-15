# Bun 源码架构总览

> 本文档基于 Bun v1.3+ 源码仓库（https://github.com/oven-sh/bun）进行分析，梳理其整体架构设计、技术选型与核心模块组织方式。

---

## 一、项目基本信息

| 属性 | 说明 |
|------|------|
| **仓库** | `oven-sh/bun` |
| **主要语言** | Zig（~70%）、C++（~20%）、TypeScript/JavaScript（~10%） |
| **核心引擎** | WebKit JavaScriptCore（JSC） |
| **构建系统** | Zig `build.zig` + CMake |
| **许可证** | MIT-like + LGPL-2（JavaScriptCore 部分） |
| **定位** | 一体化 JavaScript/TypeScript 运行时、打包器、测试运行器、包管理器 |

---

## 二、三层架构设计

Bun 采用**三层架构**，所有子系统最终汇聚到 `Zig::GlobalObject` 这个中央集成点：

```
┌─────────────────────────────────────────────────────────────┐
│                    User-Facing Layer                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────────────┐     │
│  │ CLI     │  │ REPL    │  │ Bun Global API          │     │
│  │ Interface│  │         │  │ Bun.serve(), Bun.file() │     │
│  └────┬────┘  └────┬────┘  └───────────┬─────────────┘     │
└───────┼────────────┼────────────────────┼───────────────────┘
        │            │                    │
        └────────────┴────────────────────┘
                         │
              ┌──────────▼──────────┐
              │  Zig::GlobalObject  │  ← 中央集成点
              │  extends JSC::JSGlobalObject
              └──────────┬──────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│           Execution & Tooling Layer                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ JSC      │ │ Event    │ │ Parser   │ │ Bundler      │  │
│  │ Runtime  │ │ Loop     │ │ (JS/TS)  │ │ BundleV2     │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐  │
│  │Transpiler│ │TestRunner│ │ Package Manager          │  │
│  │          │ │          │ │ (npm-compatible)         │  │
│  └──────────┘ └──────────┘ └──────────────────────────┘  │
└────────────────────────┬─────────────────────────────────────┘
                         │
┌────────────────────────┼─────────────────────────────────────┐
│              Platform Layer                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐  │
│  │ Network  │ │ File     │ │ Native       │ │ Build    │  │
│  │ I/O      │ │ System   │ │ Integration  │ │ System   │  │
│  │ HTTP/WS  │ │ src/sys  │ │ N-API, FFI   │ │ build.zig│  │
│  └──────────┘ └──────────┘ └──────────────┘ └──────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 各层职责

| 层级 | 职责 | 核心代码位置 |
|------|------|-------------|
| **用户层** | CLI 命令解析、REPL、全局 API 暴露 | `src/cli.zig`、`src/js/builtins/` |
| **执行层** | JS 执行、事件循环、解析/转换/打包/测试/包管理 | `src/bun.js/`、`src/bundler/`、`src/install/` |
| **平台层** | 底层 I/O、文件系统、网络、原生集成 | `src/sys.zig`、`src/http/`、`src/io/` |
| **核心集成** | Zig/C++/JS 三语言桥接 | `src/bun.js/bindings/ZigGlobalObject.*` |

---

## 三、源码目录结构

```
src/
├── bun.zig                    # 主入口点
├── cli.zig                    # CLI 命令编排
│
├── bun.js/                    # JavaScript 运行时核心
│   ├── bindings/              # C++ JavaScriptCore 绑定
│   │   ├── ZigGlobalObject.h  # 全局对象头文件
│   │   ├── ZigGlobalObject.cpp# 全局对象实现
│   │   ├── BunString.cpp      # 字符串桥接
│   │   └── webcore/           # Web API 绑定
│   ├── api/                   # Bun 专属 API
│   │   ├── server.zig         # HTTP 服务器
│   │   ├── FFI.zig            # 外部函数接口
│   │   ├── crypto.zig         # 加密操作
│   │   └── glob.zig           # 文件模式匹配
│   ├── node/                  # Node.js 兼容层
│   │   ├── node_fs.zig        # fs 模块
│   │   ├── node_fs_binding.zig# fs 绑定
│   │   └── types.zig          # 类型定义
│   ├── webcore/               # Web API 实现
│   │   ├── fetch.zig          # Fetch API
│   │   ├── streams.zig        # Web Streams
│   │   ├── Blob.zig           # Blob API
│   │   ├── Response.zig       # Response
│   │   └── Request.zig        # Request
│   ├── event_loop.zig         # 事件循环
│   ├── javascript.zig         # JS 执行上下文
│   ├── module_loader.zig      # 模块加载器
│   └── base.zig               # 基础类型和工具
│
├── bundler/                   # JavaScript 打包器
│   ├── bundle_v2.zig          # 打包器核心 v2
│   ├── LinkerContext.zig      # 链接上下文
│   ├── computeCrossChunkDependencies.zig  # 跨块依赖
│   ├── postProcessJSChunk.zig # JS 块后处理
│   └── renameSymbolsInChunk.zig # 符号重命名
│
├── install/                   # 包管理器
│   ├── install.zig            # 安装核心
│   ├── lockfile.zig           # 锁文件
│   ├── npm.zig                # npm 协议实现
│   ├── tarball.zig            # tarball 解压
│   └── dependency.zig         # 依赖解析
│
├── js_parser/                 # JavaScript 解析器
│   ├── js_parser.zig          # 解析器核心
│   └── js_parser_jsc/         # JSC 集成
│
├── js_printer/                # JavaScript 打印器
│   └── js_printer.zig         # 代码生成
│
├── transpiler/                # 转换器
│   └── transpiler.zig         # TS/JSX → JS
│
├── resolver/                  # 模块解析系统
│   ├── resolver.zig           # 解析器核心
│   ├── package_json.zig       # package.json 解析
│   └── resolve_path.zig       # 路径解析
│
├── http/                      # HTTP 协议栈
│   ├── http.zig               # HTTP 核心
│   └── picohttp/              # HTTP 解析器
│
├── sys/                       # 系统调用封装
│   └── sys.zig                # 文件系统/进程/网络
│
├── io/                        # I/O 抽象层
│   └── io.zig                 # io_uring / kqueue 封装
│
├── event_loop/                # 事件循环实现
│   └── event_loop.zig         # 任务调度
│
├── css/                       # CSS 处理
│   ├── css.zig                # CSS 解析
│   └── css_derive/            # CSS 派生宏
│
├── sql/                       # SQL 客户端
│   ├── sql.zig                # SQL 核心
│   └── sql_jsc/               # JSC 绑定
│
├── string/                    # 字符串工具
│   └── string.zig             # 高效字符串操作
│
├── hash/                      # 哈希算法
│   └── hash.zig               # SHA/MD5 等
│
├── allocators/                # 自定义内存分配器
│   └── bun_alloc/             # Bun 专用分配器
│
├── codegen/                   # 代码生成
│   └── bundle-modules.ts      # 内置模块打包
│
└── js/                        # 内置 JavaScript 模块
    └── builtins/              # node:fs, bun:ffi 等
```

---

## 四、核心设计哲学

### 1. 将一切视为系统编程问题

Bun 最大的创新在于**拒绝用 JavaScript 的方式解决 JavaScript 工具链的问题**。传统工具（npm、yarn）继承自 Node.js 的事件循环和线程池架构，这些优化在 2009 年（机械硬盘时代）是合理的，但在 2025 年（NVMe SSD、高速网络）已经成为瓶颈。

Bun 的核心洞察：**现代硬件的瓶颈不再是 I/O，而是系统调用（syscall）**。每次系统调用需要 1000-1500 CPU 周期的模式切换开销。Bun 通过以下方式最小化系统调用：

- 使用 Zig 直接进行系统调用，无 JavaScript 运行时开销
- 批量处理文件操作
- 利用 OS 原生文件复制机制（Linux `hardlink`、macOS `clonefile`）

### 2. 一体化设计减少通信开销

传统工具链的碎片化导致大量进程间通信开销：

```
传统流程：tsc → Babel → Webpack → Jest → npm
            ↑____多次序列化/反序列化____↑

Bun 流程：  单一进程内完成所有操作
            ↑______共享内存和缓存______↑
```

### 3. 零成本渐进式采用

Bun 不要求"全有或全无"的迁移：
- 可以单独使用 `bun install` 加速现有 Node.js 项目
- 可以单独使用 `bun test` 替代 Jest
- 可以单独使用 `bun run` 替代 `npm run`
- 最终可以完全替代 Node.js 运行时

---

## 五、技术栈选型分析

### 为什么选择 Zig？

| 候选语言 | 未选择原因 | Zig 优势 |
|----------|-----------|---------|
| **C++** | 编译慢、构建系统复杂、内存安全问题 | Zig 可直接调用 C/C++，编译更快 |
| **Rust** | 编译慢、与 C++ 互操作复杂、学习曲线陡 | Zig 与 C 互操作零成本，编译时元编程 |
| **Go** | GC 暂停、与 C++ 互操作需要 cgo 开销 | Zig 无 GC，直接内存控制 |
| **Zig** | — | 编译时执行、直接系统调用、跨平台编译 |

### 为什么选择 JavaScriptCore（JSC）而非 V8？

| 维度 | V8（Node.js/Deno） | JSC（Bun） |
|------|-------------------|-----------|
| **启动速度** | 较慢（需要初始化大量结构） | 更快（Safari 优化） |
| **内存占用** | 较高 | 更低 |
| **API 兼容性** | Chrome 标准 | Safari 标准（Web API 更一致） |
| **集成复杂度** | C++ API 复杂 | Zig 可直接调用 C API |
| **Warm-up 性能** | JIT 预热后极快 | 冷启动更优 |

Bun 的场景（CLI 工具、短生命周期脚本、HTTP 服务）更依赖**冷启动速度**，因此 JSC 是更优选择。

---

## 六、关键性能数据

| 指标 | Bun | Node.js | 倍数 |
|------|-----|---------|------|
| 包安装 | ~7-30x 更快 | 基准 | 7-30x |
| Express Hello World (RPS) | 59,026 | 19,039 | 3.1x |
| WebSocket 消息/秒 | 2,536,227 | 435,099 | 5.8x |
| PostgreSQL 查询/秒 | 28,571 | 14,522 | 2.0x |
| 启动速度 | 3x 更快 | 基准 | 3x |
| 打包 10x three.js | 269ms | esbuild: 572ms | 2.1x |

---

## 七、参考资源

- [Bun GitHub 仓库](https://github.com/oven-sh/bun)
- [Bun 官方文档](https://bun.sh/docs)
- [Bun 博客 - Behind the Scenes of Bun Install](https://bun.sh/blog/behind-the-scenes-of-bun-install)
- [Bun 博客 - The Bun Bundler](https://bun.sh/blog/bun-bundler)
- [Zig 语言官网](https://ziglang.org/)
- [WebKit JavaScriptCore](https://trac.webkit.org/wiki/JavaScriptCore)
