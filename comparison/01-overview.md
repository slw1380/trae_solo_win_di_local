# Claude Code vs Codex CLI 对比分析 - 概览

> 本文档对比分析 Anthropic 的 Claude Code 与 OpenAI 的 Codex CLI 两款 AI 编程助手工具。
> 分析日期：2026-05-14

---

## 一、产品定位

| 维度 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **开发商** | Anthropic | OpenAI |
| **发布时间** | 2025年2月（研究预览），2025年5月（GA） | 2025年4月 |
| **核心定位** | 终端 AI 编程代理（Agentic Coding） | 终端 AI 编程搭档（Pair Programming） |
| **设计理念** | Unix 哲学：专注终端，可组合、可脚本化 | 全平台覆盖：终端、IDE、云端、手机 |
| **开源状态** | 闭源（提供 SDK） | 开源（Rust 重写） |

---

## 二、核心模型

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **默认模型** | Claude Sonnet 4.5 / Opus 4.7 | GPT-5 / GPT-5-Codex |
| **模型选择** | `/model` 切换 Sonnet/Opus | `/model` 切换模型和推理级别 |
| **上下文窗口** | 最高 100 万 token | 标准 GPT-5 上下文 |
| **模型优化方向** | 代理式编码、代码库理解 | 软件工程任务、代码审查 |

---

## 三、功能特性概览

### 3.1 共同特性

- 自然语言驱动的代码编辑
- 代码库理解和导航
- Git 工作流集成
- 多文件编辑能力
- 终端交互式 REPL
- 图像输入支持
- 权限审批系统
- 非交互式/脚本化执行

### 3.2 差异化特性

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **IDE 扩展** | VS Code、JetBrains 官方扩展 | VS Code、Cursor、Windsurf 扩展 |
| **云端执行** | 不支持原生云端 | Codex Cloud 后台任务执行 |
| **代码审查** | Claude Code Security / Code Review | 原生 PR 代码审查 |
| **移动端** | 不支持 | ChatGPT iOS App 支持 |
| **沙盒机制** | 本地权限系统 | 本地沙盒 + Docker 隔离 |
| **MCP 支持** | 完整 MCP 集成（OAuth 2.0、SSE/HTTP） | MCP 支持 |
| **自定义命令** | Markdown 自定义 Slash 命令 | AGENTS.md 指令 |
| **会话管理** | 会话持久化、Teleportation | 云端状态同步 |
| **语音模式** | 支持 | 不支持 |
| **多平台 AI** | Anthropic API、AWS Bedrock、Google Vertex | OpenAI API |

---

## 四、安装与平台支持

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **macOS** | ✅ 原生支持 | ✅ 原生支持 |
| **Linux** | ✅ 原生支持 | ✅ 原生支持 |
| **Windows** | ✅ WSL 支持 | ⚠️ 实验性（推荐 WSL） |
| **安装方式** | curl / Homebrew / npm | npm / Homebrew |
| **底层语言** | 原生二进制（Rust/Go） | Rust（重写后） |

---

## 五、定价与订阅

| 特性 | Claude Code | Codex CLI |
|------|-------------|-----------|
| **包含在** | Claude Pro / Max 订阅 | ChatGPT Plus / Pro / Business / Enterprise |
| **API 计费** | 按使用量计费 | 按使用量计费 |
| **企业版** | 企业分析 API、SSO | Enterprise 计划 |

---

## 六、文档索引

- [01-overview.md](./01-overview.md) - 概览（本文档）
- [02-architecture.md](./02-architecture.md) - 架构与技术实现对比
- [03-features.md](./03-features.md) - 功能特性详细对比
- [04-workflow.md](./04-workflow.md) - 工作流程与使用场景对比
- [05-security.md](./05-security.md) - 安全与权限机制对比
- [06-ecosystem.md](./06-ecosystem.md) - 生态系统与扩展性对比
- [07-conclusion.md](./07-conclusion.md) - 总结与选型建议
