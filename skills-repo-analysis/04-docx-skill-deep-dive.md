# DOCX Skill 深度解析

> Skill 路径：https://github.com/anthropics/skills/tree/main/skills/docx
> 状态：Source-available（非开源，但公开参考）
> 用途：Claude 文件创建功能的底层实现

---

## 一、Skill 结构

```
skills/docx/
├── SKILL.md          # 主指令文件
├── scripts/          # 可执行脚本
│   └── ooxml/       # OOXML 处理脚本
│       ├── unpack.py # 解包 docx
│       └── pack.py   # 打包 docx
└── LICENSE.txt       # 专有许可证
```

---

## 二、Frontmatter 分析

```yaml
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

### 描述设计亮点

1. **能力枚举** - 列出所有功能（creation, editing, tracked changes, comments）
2. **触发场景** - "When Claude needs to work with..."
3. **具体用例** - (1)(2)(3)(4) 编号列举
4. **兜底条款** - "or any other document tasks"

---

## 三、工作流决策树

```
用户请求
    │
    ▼
┌─────────────────┐
│   任务类型判断   │
└────────┬────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
┌──────┐┌──────┐┌──────────┐
│读取/  ││创建  ││编辑现有   │
│分析   ││新文档││文档       │
└──┬───┘└──┬───┘└────┬─────┘
   │       │         │
   ▼       ▼         ▼
Text    docx-js   判断来源
extraction       ├─ 自己+简单 → Basic OOXML
Raw XML          └─ 他人/法律/学术/商业/政府 → Redlining
```

---

## 四、四大工作流详解

### 工作流一：文本提取

**工具**: pandoc

```bash
# 转换为 markdown（保留 tracked changes）
pandoc --track-changes=all path-to-file.docx -o output.md

# 选项: --track-changes=accept/reject/all
```

**适用场景**: 只需读取文本内容

### 工作流二：创建新文档

**工具**: docx-js (JavaScript/TypeScript)

**强制步骤**:
1. **MANDATORY - READ ENTIRE FILE**: 完整阅读 `docx-js.md` (~500行)
2. 使用 Document, Paragraph, TextRun 组件创建文件
3. 使用 `Packer.toBuffer()` 导出

> **关键设计**: 强制完整阅读参考文件，确保 Claude 掌握所有语法细节

### 工作流三：编辑现有文档

**工具**: Document library (Python OOXML 操作库)

**工作流**:
1. **MANDATORY - READ ENTIRE FILE**: 完整阅读 `ooxml.md` (~600行)
2. 解包: `python ooxml/scripts/unpack.py <office_file> <output_directory>`
3. 使用 Document library 创建 Python 脚本
4. 打包: `python ooxml/scripts/pack.py <input_directory> <office_file>`

### 工作流四：Redlining（文档审查）

**核心原则**: 最小化、精确的编辑

**批处理策略**: 3-10 个相关变更为一批

**精确编辑示例**:

```python
# ❌ BAD - 替换整句
'<w:del><w:r><w:delText>The term is 30 days.</w:delText></w:r></w:del>
<w:ins><w:r><w:t>The term is 60 days.</w:t></w:r></w:ins>'

# ✅ GOOD - 只标记变更，保留原始 <w:r>
'<w:r w:rsidR="00AB12CD"><w:t>The term is </w:t></w:r>
<w:del><w:r><w:delText>30</w:delText></w:r></w:del>
<w:ins><w:r><w:t>60</w:t></w:r></w:ins>
<w:r w:rsidR="00AB12CD"><w:t> days.</w:t></w:r>'
```

**Redlining 六步工作流**:

1. **获取 markdown 表示** - pandoc 转换
2. **识别和分组变更** - 按逻辑批次组织
3. **阅读文档并解包** - 强制阅读 ooxml.md
4. **批量实现变更** - 每批 3-10 个变更
5. **打包文档** - 转换回 .docx
6. **最终验证** - pandoc 转换 + grep 验证

---

## 五、关键设计模式

### 模式一：强制阅读指令

```markdown
**MANDATORY - READ ENTIRE FILE**: Read [`docx-js.md`](docx-js.md) 
(~500 lines) completely from start to finish. 
**NEVER set any range limits when reading this file.**
```

**目的**: 确保 Claude 掌握完整语法，不遗漏关键细节

### 模式二：决策树引导

通过清晰的条件判断引导 Claude 选择正确工作流：
- 读取 vs 创建 vs 编辑
- 简单编辑 vs Redlining
- 不同文档类型的处理差异

### 模式三：菜单式引用

主 SKILL.md 作为"菜单"，详细内容在引用文件中：
- `docx-js.md` - 创建文档的完整语法
- `ooxml.md` - 编辑文档的完整 API

符合渐进式加载原则，避免主文件过大。

### 模式四：精确编辑原则

Redlining 工作流的核心：
- 只标记实际变更的文本
- 保留未变更文本的原始 RSID
- 分解为: [未变更] + [删除] + [插入] + [未变更]

---

## 六、依赖管理

```markdown
## Dependencies

- **pandoc**: `sudo apt-get install pandoc` (文本提取)
- **docx**: `npm install -g docx` (创建新文档)
- **LibreOffice**: `sudo apt-get install libreoffice` (PDF 转换)
- **Poppler**: `sudo apt-get install poppler-utils` (PDF 转图片)
- **defusedxml**: `pip install defusedxml` (安全 XML 解析)
```

---

## 七、代码风格指南

```markdown
## Code Style Guidelines
**IMPORTANT**: When generating code for DOCX operations:
- Write concise code
- Avoid verbose variable names and redundant operations
- Avoid unnecessary print statements
```

---

## 八、学习要点

| 设计点 | 说明 |
|--------|------|
| **工作流决策树** | 清晰的条件分支引导正确路径 |
| **强制阅读模式** | 确保 Claude 掌握完整参考文档 |
| **渐进式加载** | 菜单式 SKILL.md + 详细引用文件 |
| **精确编辑** | 最小化变更标记，保留原始格式 |
| **批处理策略** | 3-10 个变更为一批，平衡效率与调试 |
| **验证步骤** | 最终 pandoc + grep 双重验证 |
