# Anthropic Skills 仓库深度分析 - 概览

> 仓库地址：https://github.com/anthropics/skills
> 分析日期：2026-05-14
> 仓库 Stars：134k+

---

## 仓库定位

Anthropic Skills 是 Claude 的 **Agent Skills** 官方实现仓库，包含：
- Skills 示例（创意、技术、企业、文档处理）
- Agent Skills 规范（spec）
- Skill 模板（template）
- Claude Code 插件配置

---

## 仓库结构

```
anthropics/skills/
├── .claude-plugin/          # Claude Code 插件配置
├── skills/                  # Skills 示例集合
│   ├── docx/               # Word 文档处理（生产级）
│   ├── pdf/                # PDF 处理（生产级）
│   ├── pptx/               # PPT 处理（生产级）
│   ├── xlsx/               # Excel 处理（生产级）
│   └── ...                 # 其他示例 Skills
├── spec/                    # Agent Skills 规范
│   └── agent-skills-spec.md # 规范文件（指向 agentskills.io）
├── template/                # Skill 模板
│   └── SKILL.md            # 最小化模板
├── README.md               # 仓库说明
└── THIRD_PARTY_NOTICES.md  # 第三方声明
```

---

## 核心组件

| 组件 | 说明 | 许可证 |
|------|------|--------|
| **skills/** | 示例 Skills 集合 | Apache 2.0（大部分） |
| **docx/pdf/pptx/xlsx** | 文档处理 Skills（Claude 文件功能底层） | Source-available |
| **spec/** | Agent Skills 开放规范 | 开放标准 |
| **template/** | 最小 Skill 模板 | Apache 2.0 |

---

## 关键发现

### 1. skill-creator 已不存在

原文博客提到的 `skill-creator` 目录在仓库中**已不存在**，可能已被：
- 整合到 Claude.ai 内置功能
- 替换为模板（template/）
- 迁移到独立项目

### 2. 生产级文档 Skills

仓库中包含 Claude **文件创建功能**的底层 Skills：
- `skills/docx` - Word 文档创建/编辑
- `skills/pdf` - PDF 处理
- `skills/pptx` - PPT 创建
- `skills/xlsx` - Excel 处理

这些是 **source-available**（非开源），但公开供开发者参考。

### 3. 开放标准

Agent Skills 规范已发展为开放标准：
- 官网：https://agentskills.io
- 规范文档：https://agentskills.io/specification
- 验证工具：https://github.com/agentskills/agentskills

---

## 文档索引

- [01-overview.md](./01-overview.md) - 概览（本文档）
- [02-specification.md](./02-specification.md) - Agent Skills 规范详解
- [03-template-analysis.md](./03-template-analysis.md) - Skill 模板结构分析
- [04-docx-skill-deep-dive.md](./04-docx-skill-deep-dive.md) - DOCX Skill 深度解析
- [05-plugin-system.md](./05-plugin-system.md) - Claude Code 插件系统
- [06-implementation-patterns.md](./06-implementation-patterns.md) - 实现模式总结
