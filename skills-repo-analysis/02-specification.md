# Agent Skills 规范详解

> 规范官网：https://agentskills.io/specification
> 验证工具：https://github.com/agentskills/agentskills/tree/main/skills-ref

---

## 一、目录结构规范

一个 Skill 是一个目录，至少包含 `SKILL.md` 文件：

```
skill-name/
├── SKILL.md          # 必需：元数据 + 指令
├── scripts/          # 可选：可执行代码
├── references/       # 可选：参考文档
├── assets/           # 可选：模板、资源
└── ...               # 任何额外文件或目录
```

---

## 二、SKILL.md 格式

### 基本结构

```markdown
---
name: skill-name
description: A description of what this skill does and when to use it.
---

# Skill 指令内容

## Examples
- Example usage 1

## Guidelines
- Guideline 1
```

### Frontmatter 字段

| 字段 | 必需 | 约束 | 说明 |
|------|------|------|------|
| `name` | ✅ | 1-64字符，小写+数字+连字符 | Skill 唯一标识 |
| `description` | ✅ | 1-1024字符，非空 | 描述功能和触发时机 |
| `license` | ❌ | 简短 | 许可证名称或文件引用 |
| `compatibility` | ❌ | 1-500字符 | 环境要求 |
| `metadata` | ❌ | 键值映射 | 额外元数据 |
| `allowed-tools` | ❌ | 空格分隔字符串 | 预批准工具（实验性） |

---

## 三、字段详细规范

### name 字段

**约束：**
- 仅允许小写字母（`a-z`）和连字符（`-`）
- 不能以连字符开头或结尾
- 不能包含连续连字符（`--`）
- 必须与父目录名匹配

**有效示例：**
```yaml
name: pdf-processing
name: data-analysis
name: code-review
```

**无效示例：**
```yaml
name: PDF-Processing      # ❌ 大写
name: -pdf                # ❌ 以连字符开头
name: pdf--processing     # ❌ 连续连字符
```

### description 字段

**要求：**
- 描述 Skill 做什么
- 描述何时使用它
- 包含帮助 Agent 识别相关任务的关键词

**好示例：**
```yaml
description: Extracts text and tables from PDF files, fills PDF forms, 
  and merges multiple PDFs. Use when working with PDF documents or 
  when the user mentions PDFs, forms, or document extraction.
```

**差示例：**
```yaml
description: Helps with PDFs.   # ❌ 太模糊
```

### license 字段

```yaml
license: Apache-2.0
# 或
license: Proprietary. LICENSE.txt has complete terms
```

### compatibility 字段

```yaml
compatibility: Designed for Claude Code (or similar products)
# 或
compatibility: Requires git, docker, jq, and access to the internet
# 或
compatibility: Requires Python 3.14+ and uv
```

### metadata 字段

```yaml
metadata:
  author: example-org
  version: "1.0"
```

### allowed-tools 字段（实验性）

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

---

## 四、渐进式加载机制

Agent **渐进式**加载 Skills，仅在需要时拉取更多细节：

| 层级 | 内容 | 加载时机 | 推荐大小 |
|------|------|----------|----------|
| **Metadata** | name + description | 启动时加载所有 Skills | ~100 tokens |
| **Instructions** | SKILL.md 正文 | Skill 激活时加载 | < 5000 tokens |
| **Resources** | scripts/, references/, assets/ | 需要时按需加载 | 按需 |

**关键原则：**
- 主 `SKILL.md` 保持在 **500 行以内**
- 将详细参考材料移到单独文件

---

## 五、可选目录

### scripts/

包含 Agent 可运行的可执行代码：
- 应自包含或清晰记录依赖
- 包含有用的错误消息
- 优雅处理边界情况

支持语言取决于 Agent 实现，常见选项：Python、Bash、JavaScript。

### references/

包含 Agent 可读取的额外文档：
- `REFERENCE.md` - 详细技术参考
- `FORMS.md` - 表单模板或结构化数据格式
- 领域特定文件（`finance.md`, `legal.md` 等）

保持单个参考文件聚焦。Agent 按需加载，文件越小，上下文占用越少。

### assets/

包含静态资源：
- 模板（文档模板、配置模板）
- 图片（图表、示例）
- 数据文件（查找表、模式）

---

## 六、文件引用规范

引用 Skill 内其他文件时使用**相对路径**：

```markdown
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script: scripts/extract.py
```

**约束：**
- 保持文件引用在 `SKILL.md` 一级深度
- 避免深层嵌套的引用链

---

## 七、验证工具

使用 `skills-ref` 验证 Skill：

```bash
skills-ref validate ./my-skill
```

检查内容：
- SKILL.md frontmatter 是否有效
- 是否遵循所有命名约定

---

## 八、规范核心要点

1. **最小化原则** - 最少只需 `name` + `description`
2. **渐进式披露** - 按需加载，避免上下文膨胀
3. **自包含** - Skill 目录包含所有需要的内容
4. **清晰边界** - description 明确说明何时使用、何时不使用
5. **可验证** - 提供验证工具确保规范遵循
