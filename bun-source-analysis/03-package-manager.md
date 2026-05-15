# Bun 包管理器源码架构分析

> 深入分析 `bun install` 的实现原理，包括依赖解析、锁文件系统、缓存机制、安装策略等核心模块。

---

## 一、包管理器架构概览

Bun 的包管理器是一个**独立的系统编程级实现**，使用 Zig 从零编写，不依赖 Node.js 的任何代码。其核心设计目标是将包安装视为**系统编程问题**而非 JavaScript 问题。

```
┌─────────────────────────────────────────────────────────────┐
│                     bun install 流程                        │
│                                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   │
│  │ 解析     │ → │ 解析     │ → │ 下载     │ → │ 安装     │   │
│  │package. │   │依赖树    │   │tarball  │   │到       │   │
│  │json     │   │         │   │         │   │node_modules│ │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘   │
│       │             │             │             │          │
│       ▼             ▼             ▼             ▼          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              全局缓存 (~/.bun/install/cache)         │  │
│  │  - 二进制 manifest 缓存                              │  │
│  │  - tarball 缓存                                      │  │
│  │  - 硬链接/clonefile 快速复制                          │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 二、核心性能优化原理

### 2.1 系统调用最小化

传统包管理器（npm、yarn）继承自 Node.js 的架构，在 2025 年的硬件上产生了大量不必要的系统调用：

| 包管理器 | 安装简单项目时的系统调用次数 |
|----------|---------------------------|
| yarn | ~4,000,000 |
| npm | ~1,000,000 |
| pnpm | ~500,000 |
| **Bun** | **~165,000** |

每次系统调用需要 **1000-1500 CPU 周期** 的模式切换开销。Bun 通过以下方式减少系统调用：

```zig
// Bun 直接进行系统调用（Zig）
var file = bun.sys.File.from(try bun.sys.openatA(
    bun.FD.cwd(),
    abs,
    bun.O.RDONLY,
    0,
).unwrap());

// 而非通过 Node.js 的多层封装
// fs.readFile() → libuv → 线程池 → syscall
```

### 2.2 二进制 Manifest 缓存

npm 将包的元数据（manifest）以 JSON 格式存储，每次安装都需要解析大量 JSON。Bun 将 manifest 缓存为**自定义二进制格式**：

```
npm 方式：
  registry → JSON text → JSON.parse() → JS object → 使用
  
Bun 方式：
  registry → JSON text → 解析为二进制缓存 → 直接内存映射使用
  
优势：
  - 无需重复解析 JSON
  - 可以直接 mmap 加载
  - 更小的磁盘占用
```

### 2.3 并行下载与安装

Bun 充分利用多核 CPU：

```
┌─────────────────────────────────────────┐
│           下载阶段                       │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│  │线程1│ │线程2│ │线程3│ │线程4│ ... │
│  │pkg A│ │pkg B│ │pkg C│ │pkg D│     │
│  └─────┘ └─────┘ └─────┘ └─────┘     │
│       并行 HTTP 请求（每个 CPU 核心）    │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           解压阶段                       │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐     │
│  │线程1│ │线程2│ │线程3│ │线程4│ ... │
│  │解压A│ │解压B│ │解压C│ │解压D│     │
│  └─────┘ └─────┘ └─────┘ └─────┘     │
│       并行 tarball 解压                 │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           安装阶段                       │
│  使用 hardlink/clonefile 快速复制        │
│  （无需复制文件内容）                     │
└─────────────────────────────────────────┘
```

---

## 三、依赖解析算法

### 3.1 解析流程

```
package.json
     │
     ▼
┌─────────────────┐
│ 1. 读取直接依赖  │
│ dependencies    │
│ devDependencies │
│ peerDependencies│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 递归解析      │
│ 每个依赖的       │
│ package.json    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 版本冲突处理  │
│ - Semver 匹配   │
│ - 重复依赖去重  │
│ - peerDeps 校验 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 生成依赖树    │
│ 写入 bun.lock   │
└─────────────────┘
```

### 3.2 Semver 解析

Bun 使用自定义的 Semver 解析器，针对包管理场景优化：

```zig
// src/semver/semver.zig
pub const Version = struct {
    major: u32,
    minor: u32,
    patch: u32,
    pre: []const u8,      // 预发布版本
    build: []const u8,    // 构建元数据
    
    pub fn satisfies(self: Version, range: Range) bool {
        // 优化的版本匹配，避免字符串比较
        // 使用整数比较 major/minor/patch
    }
};
```

### 3.3 依赖去重

Bun 通过**全局缓存 + 硬链接**实现依赖去重：

```
全局缓存目录 (~/.bun/install/cache)
├── react@18.2.0/
├── react@18.3.1/
├── lodash@4.17.21/
└── ...

项目 A node_modules/
├── react → hardlink → ~/.bun/install/cache/react@18.2.0
└── lodash → hardlink → ~/.bun/install/cache/lodash@4.17.21

项目 B node_modules/
├── react → hardlink → ~/.bun/install/cache/react@18.2.0  (复用！)
└── lodash → hardlink → ~/.bun/install/cache/lodash@4.17.21 (复用！)
```

---

## 四、锁文件系统

### 4.1 bun.lockb 二进制锁文件

Bun 使用**二进制格式**的锁文件（`bun.lockb`），相比 npm 的 `package-lock.json`：

| 特性 | package-lock.json | bun.lockb |
|------|------------------|-----------|
| 格式 | JSON 文本 | 自定义二进制 |
| 大小 | 大（重复字段多） | 小（约 60% 更小） |
| 解析速度 | 慢（JSON.parse） | 快（直接内存映射） |
| 可读性 | 人类可读 | 二进制（可用 `bun.lockb --print` 查看） |
| git diff | 可读 | 需配置 git diff 驱动 |

### 4.2 锁文件结构

```
bun.lockb 内部结构：
┌─────────────────┐
│ 文件头 (Header)  │
│ - 魔数          │
│ - 版本号        │
│ - 包数量        │
└─────────────────┘
┌─────────────────┐
│ 包信息表        │
│ - 包名偏移      │
│ - 版本偏移      │
│ - 依赖索引      │
│ - 校验和        │
└─────────────────┘
┌─────────────────┐
│ 字符串池        │
│ - 包名          │
│ - 版本号        │
│ - URL           │
└─────────────────┘
┌─────────────────┐
│ 依赖图          │
│ - 依赖关系索引  │
└─────────────────┘
```

### 4.3 文本锁文件支持

Bun 也支持生成文本格式的锁文件（`bun.lock`）：

```bash
# 启用文本锁文件
bun install --save-text-lockfile

# 或在 bunfig.toml 中配置
[install]
saveTextLockfile = true
```

---

## 五、缓存机制

### 5.1 三级缓存架构

```
┌─────────────────────────────────────────┐
│  L1: 内存缓存                           │
│  - 已解析的 manifest                    │
│  - 热 tarball                           │
│  - 生命周期短暂                         │
├─────────────────────────────────────────┤
│  L2: 磁盘缓存 (~/.bun/install/cache)    │
│  - 持久化 tarball                       │
│  - 二进制 manifest                      │
│  - 跨项目共享                           │
├─────────────────────────────────────────┤
│  L3: node_modules/.cache                │
│  - 编译产物缓存                         │
│  - 生命周期脚本结果                     │
└─────────────────────────────────────────┘
```

### 5.2 缓存目录结构

```
~/.bun/install/cache/
├── ${name}@${version}/          # 解压后的包内容
│   ├── package/                 # package.json
│   ├── index.js
│   └── ...
├── ${name}@${version}.tar.gz    # 原始 tarball
└── manifest/                    # 二进制 manifest 缓存
    ├── registry.npmjs.org/
    │   └── ${encoded_name}.bin
    └── ...
```

### 5.3 缓存配置

```toml
# bunfig.toml
[install.cache]
# 缓存目录
dir = "~/.bun/install/cache"

# 禁用全局缓存读取（仍可能写入 node_modules/.cache）
disable = false

# 总是从 registry 解析最新版本（忽略 manifest 缓存）
disableManifest = false
```

---

## 六、安装策略

### 6.1 文件复制后端

Bun 根据操作系统选择最快的文件复制方式：

| 后端 | 操作系统 | 原理 | 特点 |
|------|---------|------|------|
| **hardlink** | Linux, Windows | 硬链接 | 默认，零复制，共享 inode |
| **clonefile** | macOS | APFS 写时复制 | 默认，不占用额外空间 |
| **clonefile_each_dir** | macOS | 逐目录 clonefile | 更慢但更隔离 |
| **copyfile** | 全平台 | 实际复制 | 后备方案 |
| **symlink** | 全平台 | 符号链接 | 用于 `file:` 依赖 |

```bash
# 手动指定后端
bun install --backend=hardlink
bun install --backend=symlink
```

### 6.2 Hoisted vs Isolated 安装

Bun 支持两种安装策略：

```toml
# bunfig.toml
[install]
# "hoisted" - 传统方式，依赖提升到顶层（默认）
# "isolated" - 每个包独立，类似 pnpm
linker = "hoisted"
```

**Hoisted 模式：**
```
node_modules/
├── react/              ← 提升的依赖
├── react-dom/
├── lodash/
└── my-package/
    └── node_modules/
        └── (peer deps)
```

**Isolated 模式：**
```
node_modules/
├── .store/
│   ├── react@18.2.0/
│   ├── react-dom@18.2.0/
│   └── lodash@4.17.21/
└── my-package/
    └── node_modules/
        ├── react → ../../.store/react@18.2.0
        └── lodash → ../../.store/lodash@4.17.21
```

---

## 七、生命周期脚本安全

### 7.1 默认不执行策略

与其他包管理器不同，Bun **默认不执行**依赖包的生命周期脚本（`postinstall` 等）：

```
npm/yarn: 安装包 → 自动执行 postinstall
Bun:      安装包 → 跳过 postinstall（更安全）
```

### 7.2 Trusted Dependencies

需要执行生命周期脚本的包必须显式声明：

```json
{
  "name": "my-app",
  "trustedDependencies": [
    "sharp",
    "esbuild",
    "node-sass"
  ]
}
```

### 7.3 并发执行

允许执行的脚本会**并行运行**：

```toml
# bunfig.toml
[install]
# 最大并发生命周期脚本数（默认 CPU 核心数 x2）
concurrentScripts = 16
```

---

## 八、核心源码文件

| 功能 | 核心文件 |
|------|---------|
| 安装主流程 | `src/install/install.zig` |
| 锁文件 | `src/install/lockfile.zig` |
| npm 协议 | `src/install/npm.zig` |
| tarball 处理 | `src/install/tarball.zig` |
| 依赖解析 | `src/install/dependency.zig` |
| Semver | `src/semver/semver.zig` |
| 系统调用 | `src/sys/sys.zig` |
| 缓存管理 | `src/cache.zig` |
| 文件系统 | `src/fs.zig` |

---

## 九、与 npm/pnpm/yarn 的架构对比

| 维度 | npm | yarn | pnpm | Bun |
|------|-----|------|------|-----|
| **实现语言** | JavaScript | JavaScript | JavaScript | Zig |
| **运行时依赖** | Node.js | Node.js | Node.js | 无（独立可执行） |
| **系统调用** | 间接（libuv） | 间接（libuv） | 间接（libuv） | 直接 |
| **锁文件格式** | JSON | YAML | YAML | 二进制 |
| **缓存策略** | 本地缓存 | 全局缓存 | 全局存储 | 全局缓存+硬链接 |
| **安装速度** | 基准 | 慢 | 快 | 最快 |
| **生命周期脚本** | 默认执行 | 默认执行 | 默认执行 | 默认不执行 |
| **并发模型** | 单线程+线程池 | 单线程+线程池 | 单线程+线程池 | 多线程并行 |

---

## 十、参考资源

- [Bun Install Docs](https://bun.sh/docs/cli/install)
- [Behind the Scenes of Bun Install](https://bun.sh/blog/behind-the-scenes-of-bun-install)
- [Bun Lockfile](https://bun.sh/docs/install/lockfile)
- [Bun Cache](https://bun.sh/docs/install/cache)
