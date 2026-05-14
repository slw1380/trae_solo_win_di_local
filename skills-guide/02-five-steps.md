# Claude Skills 创建指南 - 五步创建法

---

## 概述

创建 Skill 需要遵循结构化方法，确保 Skill 能够被可靠触发并产生预期输出。以下是五个核心步骤。

---

## 步骤一：理解核心需求

在编写任何内容之前，先明确你的 Skill 解决什么问题。

### 强 Skill 的特征

- 解决**具体需求**
- 有**可衡量的结果**

### 示例对比

| 弱描述 | 强描述 |
|--------|--------|
| "Help with my finance stuff" | "Extract financial data from PDFs and format as CSV" |

强描述明确了：输入格式（PDF）、操作（提取数据）、预期输出（CSV）。

### 自问清单

1. 这个 Skill 完成什么**具体任务**？
2. 什么**触发条件**应该激活它？
3. **成功标准**是什么？
4. 有哪些**边界情况或限制**？

---

## 步骤二：编写名称

Skill 需要三个核心组件：

| 组件 | 作用 | 说明 |
|------|------|------|
| **name** | 清晰标识符 | 小写 + 连字符，如 `pdf-editor` |
| **description** | 何时激活 | 最关键组件，决定触发时机 |
| **instructions** | 如何执行 | 详细的执行指南 |

### 命名规范

- 使用**小写字母** + **连字符**
- 保持**简短清晰**
- 示例：`pdf-editor`、`brand-guidelines`

> **重要**: name 和 description 是 SKILL.md 文件中**唯一影响触发**的部分。Claude 通过它们判断是否需要调用 Skill 获取专业知识或工作流。

---

## 步骤三：编写描述字段

**描述字段是决定 Skill 何时激活的最关键组件。**

### 编写视角

从 **Claude 的视角** 编写，聚焦：
- 触发条件
- 能力范围
- 使用场景

### 强弱描述对比

**弱描述：**
```
This skill helps with PDFs and documents.
```

**强描述：**
```
Comprehensive PDF manipulation toolkit for extracting text and tables, 
creating new PDFs, merging/splitting documents, and handling forms. 
When Claude needs to fill in a PDF form or programmatically process, 
generate, or analyze PDF documents at scale. Use for document workflows 
and batch operations. Not for simple PDF viewing or basic conversions.
```

### 强描述的要素

| 要素 | 说明 |
|------|------|
| **具体动词** | extract, create, merge |
| **具体用例** | form filling, batch operations |
| **清晰边界** | Not for simple viewing |

---

## 步骤四：编写主指令

指令应该**结构化、可扫描、可操作**。

### 格式规范

- 使用 Markdown 标题组织层次
- 使用项目符号列出选项
- 使用代码块展示示例

### 推荐结构

```markdown
## Overview
概述 Skill 的功能和适用场景

## Prerequisites
前置条件和依赖

## Execution Steps
执行步骤（分阶段，明确输入输出）

## Examples
具体示例展示正确用法

## Error Handling
错误处理方法

## Limitations
明确 Skill 不能做什么
```

### 关键原则

1. **分阶段** - 将复杂工作流拆分为离散阶段
2. **明确输入输出** - 每个阶段都有清晰的输入和输出
3. **包含具体示例** - 展示正确用法
4. **说明限制** - 防止误用，管理预期
5. **附加参考文件** - SKILL.md 可包含额外的参考文件和资源

---

## 步骤五：上传 Skill

根据使用平台，有三种上传方式：

### 方式一：Claude.ai（Claude Apps）

- 进入 **Settings**
- 添加自定义 Skill
- 要求：Pro、Max、Team 或 Enterprise 计划，且启用代码执行
- **注意**：个人用户级别，不共享给组织

### 方式二：Claude Code

在项目根目录创建 `skills/` 目录：

```
my-project/
├── skills/
│   └── my-skill/
│       └── SKILL.md
```

Claude 安装插件后会自动发现和使用。

### 方式三：Claude Developer Platform（API）

通过 Skills API 上传：

```bash
curl -X POST "https://api.anthropic.com/v1/skills" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "display_title=My Skill Name" \
  -F "files[]=@my-skill/SKILL.md;filename=my-skill/SKILL.md"
```

---

## 五步流程图

```
┌─────────────────┐
│ 1. 理解核心需求  │
│   明确问题边界   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. 编写名称      │
│   小写+连字符    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. 编写描述      │
│   最关键组件     │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 4. 编写主指令    │
│   结构化可执行   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 5. 上传部署      │
│   三平台可选     │
└─────────────────┘
```
