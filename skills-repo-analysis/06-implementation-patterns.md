# Skills 实现模式总结

---

## 模式一：最小化 Skill

**适用**: 简单任务，< 100 行指令

```
simple-skill/
└── SKILL.md
```

**特点**:
- 单文件
- 仅必需 frontmatter
- 直接指令

---

## 模式二：结构化 Skill

**适用**: 中等复杂度，明确步骤

```
structured-skill/
└── SKILL.md
```

**内容结构**:
```markdown
---
name: structured-skill
description: ...
---

# Overview
## Prerequisites
## Execution Steps
## Examples
## Error Handling
## Limitations
```

**特点**:
- 清晰的章节划分
- 包含示例和边界说明
- 自包含

---

## 模式三：菜单式 Skill

**适用**: 复杂任务，多路径工作流

```
menu-skill/
├── SKILL.md          # 菜单：描述选项
├── references/
│   ├── path-a.md     # 路径 A 详情
│   └── path-b.md     # 路径 B 详情
└── scripts/
    ├── helper-a.py
    └── helper-b.py
```

**SKILL.md 结构**:
```markdown
# Menu Skill

## Available Workflows
- **Workflow A**: For scenario X. See [path-a.md](references/path-a.md)
- **Workflow B**: For scenario Y. See [path-b.md](references/path-b.md)

## Decision Tree
Scenario X → Use Workflow A
Scenario Y → Use Workflow B
```

**特点**:
- 主文件作为目录/菜单
- 详细内容按需加载
- 符合渐进式披露原则

---

## 模式四：工具型 Skill

**适用**: 需要执行代码的任务

```
tool-skill/
├── SKILL.md
├── scripts/
│   ├── extract.py
│   ├── transform.py
│   └── validate.py
└── assets/
    └── template.json
```

**特点**:
- 包含可执行脚本
- 脚本自包含或清晰记录依赖
- 可能包含模板/资源文件

---

## 模式五：参考密集型 Skill

**适用**: 需要大量领域知识的任务

```
knowledge-skill/
├── SKILL.md
└── references/
    ├── REFERENCE.md      # 详细技术参考
    ├── api-reference.md  # API 文档
    ├── examples.md       # 更多示例
    └── best-practices.md # 最佳实践
```

**特点**:
- 主文件保持精简
- 知识库在 references/ 中
- Agent 按需读取

---

## 模式六：生产级 Skill（DOCX 模式）

**适用**: 复杂、多工作流、生产环境

```
production-skill/
├── SKILL.md              # 决策树 + 工作流概述
├── scripts/
│   └── tool-suite/
│       ├── unpack.py
│       └── pack.py
├── references/
│   ├── library-a.md      # 库 A 完整文档
│   └── library-b.md      # 库 B 完整文档
└── LICENSE.txt
```

**特点**:
- 决策树引导正确工作流
- 强制完整阅读参考文件
- 精确的错误处理
- 验证步骤
- 代码风格指南

---

## 模式选择决策树

```
任务复杂度评估
    │
    ▼
简单 (< 100行指令)?
    │
   YES → 模式一：最小化 Skill
    │
   NO → 需要多路径?
            │
           YES → 模式三：菜单式 Skill
            │
           NO → 需要执行代码?
                    │
                   YES → 模式四：工具型 Skill
                    │
                   NO → 需要大量领域知识?
                            │
                           YES → 模式五：参考密集型
                            │
                           NO → 模式二：结构化 Skill
```

---

## 设计原则总结

| 原则 | 说明 |
|------|------|
| **最小开始** | 从模板开始，按需扩展 |
| **渐进披露** | 主文件精简，细节按需加载 |
| **自包含** | 一个目录包含所有需要的内容 |
| **清晰边界** | description 明确何时使用、何时不用 |
| **可验证** | 提供测试和验证方法 |
| **决策引导** | 复杂 Skill 用决策树引导正确路径 |

---

## 常见反模式

| 反模式 | 问题 | 解决方案 |
|--------|------|----------|
| **巨型 SKILL.md** | 上下文膨胀 | 拆分为 references/ |
| **模糊描述** | 触发不准确 | 具体动词 + 用例 + 边界 |
| **缺少示例** | 输出不一致 | 包含具体输入输出示例 |
| **无错误处理** | 边界情况崩溃 | 说明错误处理方法 |
| **深层引用链** | 加载复杂 | 保持一级深度引用 |
