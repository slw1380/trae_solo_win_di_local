# Bun 源码架构分析文档集

> 本目录包含对 Bun（https://github.com/oven-sh/bun）源码架构的系统性分析文档，基于 Bun v1.3+ 版本。

---

## 文档结构

| 文档 | 内容 | 文件 |
|------|------|------|
| **总览** | Bun 整体架构、技术选型、源码目录结构 | [01-overview.md](01-overview.md) |
| **运行时** | JavaScript 运行时、JSC 集成、模块系统、事件循环、Node.js 兼容层 | [02-runtime.md](02-runtime.md) |
| **包管理器** | bun install 实现、依赖解析、锁文件、缓存机制、安装策略 | [03-package-manager.md](03-package-manager.md) |
| **打包器** | Bundler 实现、解析/链接/代码生成、Tree Shaking、CSS 处理、插件系统 | [04-bundler.md](04-bundler.md) |
| **测试运行器** | bun test 实现、测试发现/执行、Expect API、快照、覆盖率 | [05-test-runner.md](05-test-runner.md) |
| **底层技术栈** | Zig 语言特性、JavaScriptCore 架构、Zig↔JSC 集成机制 | [06-zig-jsc-integration.md](06-zig-jsc-integration.md) |

---

## 阅读建议

1. **快速了解**：先阅读 [01-overview.md](01-overview.md) 了解整体架构
2. **深入运行时**：阅读 [02-runtime.md](02-runtime.md) 和 [06-zig-jsc-integration.md](06-zig-jsc-integration.md)
3. **包管理**：阅读 [03-package-manager.md](03-package-manager.md)
4. **构建工具**：阅读 [04-bundler.md](04-bundler.md)
5. **测试框架**：阅读 [05-test-runner.md](05-test-runner.md)

---

## 核心架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    User-Facing Layer                        │
│              CLI / REPL / Bun Global API                    │
└─────────────────────────┬───────────────────────────────────┘
                          │
               ┌──────────▼──────────┐
               │  Zig::GlobalObject  │  ← 中央集成点
               │  extends JSGlobalObject│
               └──────────┬──────────┘
                          │
    ┌─────────────────────┼─────────────────────┐
    │                     │                     │
┌───▼───┐          ┌─────▼─────┐          ┌────▼────┐
│ JSC   │          │  Bun API  │          │ Node.js │
│ 引擎  │          │  绑定层   │          │ 兼容层  │
│       │          │ (Zig)     │          │ (Zig)   │
└───────┘          └───────────┘          └─────────┘
    │                     │                     │
    └─────────────────────┼─────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│              Execution & Tooling Layer                     │
│  Runtime │ Bundler │ Transpiler │ TestRunner │ PackageMgr │
└─────────────────────────┬─────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────┐
│                   Platform Layer                           │
│         Network I/O │ File System │ Native Integration     │
└─────────────────────────────────────────────────────────────┘
```

---

## 参考资源

- [Bun GitHub 仓库](https://github.com/oven-sh/bun)
- [Bun 官方文档](https://bun.sh/docs)
- [Bun 博客](https://bun.sh/blog)
- [Zig 语言官网](https://ziglang.org/)
- [WebKit JavaScriptCore](https://trac.webkit.org/wiki/JavaScriptCore)
