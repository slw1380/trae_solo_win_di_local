# Bun 与 npm 对比及 Bun 配置指南

> 本文档基于 Bun v1.3+ 与 npm 的最新特性整理，帮助开发者了解两者的核心差异以及如何在项目中配置和使用 Bun。

---

## 一、Bun 与 npm 核心对比

### 1. 定位差异

| 维度 | npm | Bun |
|------|-----|-----|
| **定位** | Node.js 官方包管理器 | 一体化 JavaScript/TypeScript 工具链（运行时 + 包管理器 + 打包器 + 测试运行器） |
| **安装方式** | 随 Node.js 一起安装 | 独立安装，可单独使用 |
| **兼容性** | Node.js 原生 | 目标 100% Node.js 兼容，可渐进式采用 |
| **配置方式** | `.npmrc`、`package.json` | `bunfig.toml`、`package.json`、环境变量、CLI 参数 |

### 2. 性能对比

Bun 在多个场景下显著快于 npm：

| 场景 | Bun | npm | 倍数 |
|------|-----|-----|------|
| **包安装速度** | ~7-30x 更快 | 基准 | 7-30 倍 |
| **Express.js Hello World (RPS)** | 59,026 | 19,039 | ~3.1 倍 |
| **WebSocket 消息/秒** | 2,536,227 | 435,099 | ~5.8 倍 |
| **PostgreSQL 查询/秒** | 28,571 | 14,522 | ~2.0 倍 |
| **启动速度** | 3x 更快 | 基准 | 3 倍 |

> 性能优势来源：Bun 使用 Zig 编写底层，采用 JavaScriptCore 引擎，并将包安装视为系统编程问题（最小化系统调用、并行下载、硬链接缓存等）。

### 3. 功能对比

| 功能 | npm | Bun |
|------|-----|-----|
| **包管理** | 支持 | 支持，且更快 |
| **运行时** | Node.js 本身 | 内置，可替代 Node.js |
| **TypeScript 支持** | 需 ts-node 等工具 | 原生支持，零配置 |
| **JSX 支持** | 需 Babel/编译器 | 原生支持，零配置 |
| **打包构建** | 需 Webpack/Vite/esbuild | 内置 `bun build` |
| **测试运行器** | 需 Jest/Vitest | 内置 `bun test` |
| **脚本运行** | `npm run` | `bun run`，更快 |
| **锁文件** | `package-lock.json`（文本） | `bun.lockb`（二进制，更小更快） |
| **全局缓存** | 有 | 有，路径 `~/.bun/install/cache` |
| **工作区 (Workspaces)** | 支持 | 支持 |
| **生命周期脚本安全** | 默认执行 | 默认不执行，需加入 `trustedDependencies` |

### 4. 命令对比速查

| 操作 | npm | Bun |
|------|-----|-----|
| 安装所有依赖 | `npm install` | `bun install` |
| 添加依赖 | `npm install <pkg>` | `bun add <pkg>` |
| 添加开发依赖 | `npm install -D <pkg>` | `bun add -d <pkg>` |
| 移除依赖 | `npm uninstall <pkg>` | `bun remove <pkg>` |
| 运行脚本 | `npm run <script>` | `bun run <script>` |
| 执行包 | `npx <pkg>` | `bunx <pkg>` |
| 初始化项目 | `npm init` | `bun init` |
| 全局安装 | `npm install -g <pkg>` | `bun install -g <pkg>` |
| 生产环境安装 | `npm install --production` | `bun install --production` |
| 锁定安装 | `npm ci` | `bun install --frozen-lockfile` |
| 运行测试 | `npm test` | `bun test` |
| 构建打包 | 需额外工具 | `bun build ./index.ts --outdir ./dist` |
| 运行文件 | `node index.js` | `bun index.js` 或 `bun ./index.ts` |

---

## 二、Bun 安装方法

### 1. macOS / Linux

```bash
# 官方推荐方式
curl -fsSL https://bun.sh/install | bash

# 安装完成后，将 bun 加入 PATH（根据安装提示执行）
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
```

### 2. Windows

```powershell
# PowerShell
powershell -c "irm bun.sh/install.ps1 | iex"
```

### 3. 通过包管理器安装

```bash
# Homebrew (macOS/Linux)
brew install oven-sh/bun/bun

# Docker
docker pull oven/bun

# npm（不推荐，仅作为备选）
npm install -g bun
```

### 4. 验证安装

```bash
bun --version
```

---

## 三、Bun 配置详解（bunfig.toml）

Bun 使用 `bunfig.toml` 作为配置文件，支持**项目级**（`./bunfig.toml`）和**全局级**（`$HOME/.bunfig.toml` 或 `$XDG_CONFIG_HOME/.bunfig.toml`）。两者同时存在时会浅合并，本地配置优先。

### 1. 包管理配置 `[install]`

```toml
[install]
# 默认镜像源
registry = "https://registry.npmjs.org"

# 生产模式（不安装 devDependencies）
production = false

# 是否保存文本格式锁文件（替代二进制 bun.lockb）
saveTextLockfile = false

# 禁止修改锁文件（CI 推荐开启）
frozenLockfile = false

# 模拟安装，不实际写入
dryRun = false

# 是否安装 optionalDependencies
optional = true

# 是否安装 devDependencies
dev = true

# 是否安装 peerDependencies
peer = true

# 最大并发生命周期脚本数（默认 CPU 核心数 x2）
concurrentScripts = 16

# 全局安装目录
globalDir = "~/.bun/install/global"

# 全局可执行文件链接目录
globalBinDir = "~/.bun/bin"

# 安装策略: "hoisted" 或 "isolated"
linker = "hoisted"
```

### 2. 缓存配置 `[install.cache]`

```toml
[install.cache]
# 缓存目录
dir = "~/.bun/install/cache"

# 是否禁用全局缓存读取
disable = false

# 是否总是从 registry 解析最新版本
disableManifest = false
```

### 3. 锁文件配置 `[install.lockfile]`

```toml
[install.lockfile]
# 是否保存锁文件
save = true

# 输出 yarn v1 格式的 lockfile（仅转换，不读取）
print = "yarn"
```

### 4. 私有镜像 / 作用域配置 `[install.scopes]`

```toml
[install.scopes]
# 方式1：仅指定镜像地址
"@mycompany" = "https://registry.mycompany.com"

# 方式2：带认证 Token
"@mycompany" = { token = "123456", url = "https://registry.mycompany.com" }

# 方式3：使用环境变量
"@mycompany" = { token = "$NPM_TOKEN", url = "https://registry.mycompany.com" }

# 方式4：Basic Auth（用户名+密码）
"@mycompany" = { username = "user", password = "$NPM_PASSWORD", url = "https://registry.mycompany.com" }

# 方式5：URL 中直接嵌入认证信息
"@mycompany" = "https://username:password@registry.mycompany.com"
```

### 5. 运行时配置（顶层字段）

```toml
# 预加载脚本/插件
preload = ["./preload.ts"]

# JSX 配置
jsx = "react"
jsxFactory = "h"
jsxFragment = "Fragment"
jsxImportSource = "react"

# 降低内存占用模式（牺牲性能）
smol = false

# 日志级别: debug | warn | error
logLevel = "warn"

# 禁用自动加载 .env
env = false

# 或指定 .env 文件
[env]
file = ".env.production"

# 文件扩展名映射到加载器
[loader]
".bagel" = "tsx"

# 禁用遥测/崩溃报告
telemetry = false

# console.log 对象展开深度
[console]
depth = 3

# 全局变量替换（类似 webpack DefinePlugin）
[define]
"process.env.API_URL" = "'https://api.example.com'"
```

### 6. 测试配置 `[test]`

```toml
[test]
# 是否启用覆盖率
coverage = false

# 覆盖率输出目录
coverageDirectory = "coverage"

# 覆盖率报告格式
coverageReporter = ["text", "lcov"]

# 跳过测试文件本身的覆盖率
coverageSkipTestFiles = true

# 排除路径
coveragePathIgnorePatterns = [
  "**/node_modules/**",
  "**/dist/**",
  "**/.bun/**",
]

# 启用 dots 报告器（紧凑输出）
[test.reporter]
dots = true

# JUnit XML 报告
[test.reporter.junit]
enabled = true
output = "./test-results.xml"
```

### 7. Serve 配置 `[serve]`

```toml
[serve]
# 默认端口
port = 3000

# 默认主机
host = "localhost"

# 开发模式（影响错误页面等）
dev = true
```

### 8. 完整配置示例

```toml
# bunfig.toml - 完整示例
# 文档: https://bun.sh/docs/runtime/bunfig

# ========== 运行时 ==========
preload = ["./src/polyfills.ts"]
jsx = "react-jsx"
jsxImportSource = "react"
smol = false
logLevel = "warn"
telemetry = false

[env]
file = ".env"

[loader]
".svg" = "text"
".wasm" = "wasm"

[define]
"process.env.NODE_ENV" = "'development'"

# ========== 包管理 ==========
[install]
registry = "https://registry.npmjs.org"
production = false
frozenLockfile = false
optional = true
dev = true
peer = true
concurrentScripts = 16
linker = "hoisted"

[install.cache]
dir = "~/.bun/install/cache"
disable = false
disableManifest = false

[install.lockfile]
save = true

# 私有包镜像示例
[install.scopes]
"@mycompany" = { token = "$NPM_TOKEN", url = "https://registry.mycompany.com" }

# ========== 测试 ==========
[test]
coverage = false
coverageDirectory = "coverage"
coverageReporter = ["text", "lcov"]
coverageSkipTestFiles = true

# ========== Serve ==========
[serve]
port = 3000
host = "0.0.0.0"
```

---

## 四、环境变量配置

除了 `bunfig.toml`，Bun 还支持通过环境变量进行配置：

| 环境变量 | 说明 |
|----------|------|
| `BUN_INSTALL` | Bun 安装目录 |
| `BUN_INSTALL_CACHE_DIR` | 包缓存目录 |
| `BUN_CONFIG_REGISTRY` | 默认镜像源 |
| `BUN_CONFIG_TOKEN` | 镜像认证 Token |
| `BUN_CONFIG_LINK_NATIVE_BINS` | 是否链接原生二进制文件 |
| `DO_NOT_TRACK` | 禁用遥测（等价于 `telemetry = false`） |

---

## 五、package.json 中的 Bun 专属配置

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "trustedDependencies": [
    "sharp",
    "esbuild"
  ],
  "overrides": {
    "lodash": "^4.17.21"
  },
  "workspaces": [
    "packages/*"
  ]
}
```

- `trustedDependencies`：允许执行这些包的生命周期脚本（如 `postinstall`）
- `overrides` / `resolutions`：覆盖间接依赖的版本
- `workspaces`：Monorepo 工作区支持

---

## 六、迁移建议

### 何时使用 Bun？

- 追求更快的安装速度和构建速度
- 希望减少工具链复杂度（一个工具替代多个）
- 新项目，希望原生支持 TypeScript/JSX
- 需要高性能的 HTTP 服务或 WebSocket 服务

### 何时继续使用 npm？

- 已有大型项目，依赖复杂，迁移成本高
- 团队对 Bun 不够熟悉，需要稳定的生态
- 某些原生模块在 Bun 上兼容性有问题
- 需要特定的 npm 生态工具链

### 渐进式迁移策略

1. **第一步**：在现有 Node.js 项目中单独使用 `bun install` 替代 `npm install`
2. **第二步**：使用 `bun run` 替代 `npm run` 执行脚本
3. **第三步**：使用 `bun test` 替代 Jest/Vitest
4. **第四步**：使用 `bun build` 替代 Webpack/Vite（如适用）
5. **第五步**：完全使用 `bun` 作为运行时替代 `node`

---

## 七、参考资源

- [Bun 官方文档](https://bun.sh/docs)
- [bunfig.toml 完整配置参考](https://bun.sh/docs/runtime/bunfig)
- [bun install 文档](https://bun.sh/docs/cli/install)
- [Bun GitHub 仓库](https://github.com/oven-sh/bun)
