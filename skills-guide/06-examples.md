# Claude Skills 创建指南 - 真实案例解析

---

## 案例一：DOCX 文档处理 Skill

### 来源

[GitHub - anthropics/skills/document-skills/docx](https://github.com/anthropics/skills/tree/main/document-skills/docx)

### Skill 结构

```markdown
---
name: docx
description: "Comprehensive document creation, editing, and analysis 
with support for tracked changes, comments, formatting preservation, 
and text extraction. When Claude needs to work with professional 
documents (.docx files) for: (1) Creating new documents, 
(2) Modifying or editing content, (3) Working with tracked changes, 
(4) Adding comments, or any other document tasks"
license: Proprietary. LICENSE.txt has complete terms
---
```

### 工作流决策树

```
                    ┌─────────────────┐
                    │   用户请求       │
                    └────────┬────────┘
                             ▼
              ┌────────────────────────────┐
              │      任务类型判断           │
              └─────────────┬──────────────┘
                            ▼
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
   ┌─────────┐      ┌─────────────┐      ┌─────────────┐
   │ 读取/分析 │      │  创建新文档  │      │  编辑现有文档 │
   └────┬────┘      └──────┬──────┘      └──────┬──────┘
        ▼                  ▼                    ▼
   Text extraction     docx-js workflow    判断文档来源
   Raw XML access                         ├─ 自己的文档+简单修改 → Basic OOXML
                                          └─ 他人文档/法律/学术/商业/政府 → Redlining
```

### 关键工作流详解

#### 1. 文本提取

```bash
# 使用 pandoc 转换为 markdown
pandoc --track-changes=all path-to-file.docx -o output.md
# 选项: --track-changes=accept/reject/all
```

#### 2. 创建新文档

**工具**: docx-js (JavaScript/TypeScript)

**工作流**:
1. **必须**完整阅读 `docx-js.md` (~500行)
2. 使用 Document, Paragraph, TextRun 组件创建 JS/TS 文件
3. 使用 `Packer.toBuffer()` 导出 .docx

#### 3. 编辑现有文档

**工具**: Document library (Python OOXML 操作库)

**工作流**:
1. **必须**完整阅读 `ooxml.md` (~600行)
2. 解包文档: `python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. 使用 Document library 创建 Python 脚本
4. 打包最终文档: `python ooxml/scripts/pack.py <input_directory> <office_file>`

#### 4. Redlining 工作流（文档审查）

**核心原则**: 最小化、精确的编辑

**批处理策略**: 将相关变更分组为 3-10 个变更的批次

**示例** - 将 "30 days" 改为 "60 days":

```python
# ❌ BAD - 替换整句
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del>
<w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# ✅ GOOD - 只标记变更部分，保留原始 <w:r>
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r>
<w:del><w:r><w:delText>30</w:delText></w:r></w:del>
<w:ins><w:r><w:t>60</w:t></w:r></w:ins>
<w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

**定位方法**（在 XML 中查找变更位置）:
- 章节/标题编号 (如 "Section 3.2", "Article IV")
- 段落标识符（如有编号）
- 带唯一周围文本的 Grep 模式
- 文档结构 (如 "first paragraph", "signature block")
- **不要使用 markdown 行号** - 它们不映射到 XML 结构

---

## 案例学习要点

### 1. 描述的力量

DOCX Skill 的描述：
- 列出具体能力（creation, editing, tracked changes, comments）
- 明确触发场景（4 种具体场景）
- 使用 "When Claude needs to..." 句式

### 2. 工作流决策树

通过清晰的决策树引导 Claude 选择正确的工作流：
- 读取 vs 创建 vs 编辑
- 简单编辑 vs Redlining
- 不同文档类型的处理差异

### 3. 强制阅读模式

使用 **MANDATORY - READ ENTIRE FILE** 指令确保 Claude 完整阅读参考文件：
- 不设置范围限制
- 完整阅读以获取详细语法和最佳实践

### 4. 精确编辑原则

Redlining 工作流展示了精确编辑的重要性：
- 只标记实际变更的文本
- 保留未变更文本的原始 RSID
- 分解为: [未变更] + [删除] + [插入] + [未变更]

---

## 案例二：Skill Creator 本身

### 来源

[GitHub - anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator)

### 功能

- 引导用户创建结构良好的 Skill
- 提出澄清问题
- 建议描述改进
- 帮助格式化指令

### 设计亮点

1. **交互式引导** - 通过提问澄清需求
2. **模板化输出** - 生成标准化的 SKILL.md
3. **最佳实践内置** - 自动应用描述和指令的最佳实践

---

## 案例总结

| 案例 | 核心学习点 |
|------|-----------|
| **DOCX Skill** | 复杂工作流的结构化、决策树设计、精确编辑 |
| **Skill Creator** | 交互式引导、模板化、最佳实践内置 |
