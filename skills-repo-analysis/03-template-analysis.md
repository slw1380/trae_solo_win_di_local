# Skill 模板结构分析

> 模板路径：https://github.com/anthropics/skills/tree/main/template

---

## 模板内容

```markdown
---
name: template-skill
description: Replace with description of the skill and when Claude should use it.
---
# Insert instructions below
```

---

## 模板分析

### 极简设计

模板仅包含**必需的 frontmatter 字段**：
- `name` - 占位符：`template-skill`
- `description` - 占位说明

### 设计意图

1. **零门槛** - 只需替换两个字段即可创建基本 Skill
2. **无预设结构** - 不强制特定的指令组织方式
3. **渐进增强** - 从最小开始，按需添加复杂度

---

## 从模板到生产 Skill 的演进

### 阶段一：最小 Skill

```markdown
---
name: my-skill
description: What this skill does and when to use it.
---

# My Skill

Instructions here.
```

### 阶段二：结构化 Skill

```markdown
---
name: my-skill
description: Detailed description with triggers and boundaries.
license: Apache-2.0
---

# My Skill

## Overview
Brief description of what this skill does.

## Prerequisites
What needs to be in place before using this skill.

## Execution Steps
1. Step one
2. Step two
3. Step three

## Examples
### Example 1: Basic usage
```
Input: ...
Output: ...
```

### Example 2: Advanced usage
```
Input: ...
Output: ...
```

## Error Handling
How to handle common errors.

## Limitations
What this skill cannot do.
```

### 阶段三：复杂 Skill（带资源）

```
my-skill/
├── SKILL.md              # 主指令（菜单式）
├── scripts/
│   ├── extract.py        # 数据提取脚本
│   └── transform.py      # 数据转换脚本
├── references/
│   ├── REFERENCE.md      # 详细 API 参考
│   └── FORMS.md          # 表单模板
└── assets/
    ├── template.docx     # 文档模板
    └── logo.png          # 品牌资源
```

---

## 模板 vs 实际 Skills 对比

| 维度 | 模板 | 实际 Skill（如 docx） |
|------|------|----------------------|
| **frontmatter** | 仅 name + description | 包含 license 等 |
| **正文长度** | 1 行 | 数百行 |
| **目录结构** | 单文件 | 多目录 + 多文件 |
| **脚本** | 无 | 有 |
| **参考文件** | 无 | 有 |

---

## 模板使用建议

### 何时使用模板

- 快速原型验证
- 第一个 Skill 的创建
- 简单任务（< 100 行指令）

### 何时超越模板

- 需要脚本执行
- 指令超过 500 行
- 需要参考文档
- 多路径工作流

---

## 模板设计哲学

> **Skills are simple to create** - just a folder with a `SKILL.md` file.

Anthropic 的设计哲学：
1. **简单开始** - 最小化门槛
2. **按需扩展** - 不简单时再加复杂度
3. **自包含** - 一个目录搞定一切
4. **渐进披露** - 加载时按需拉取
