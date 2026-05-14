# Claude Skills 创建指南 - 最佳实践

---

## 一、从用例出发

### 不要投机性创建

**原则**：有真实、重复的任务时再构建 Skill。

### 判断标准

在创建 Skill 前，问自己：

1. 这个任务我是否至少做过 **5 次**？
2. 我是否还会再做至少 **10 次**？

如果两个答案都是"是"，那么创建 Skill 是有意义的。

---

## 二、定义成功标准并纳入 Skill

### 告诉 Claude 什么是好的输出

**示例**：创建财务报告 Skill

在指令中包含：
- 必需章节
- 格式标准
- 验证检查
- 质量阈值

这样 Claude 可以**自我检查**输出质量。

---

## 三、使用 Skill-Creator Skill

### 官方推荐工具

- **仓库**: [GitHub - anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator)
- **Claude.ai 直接使用**: 在 Claude.ai 中调用

### 功能

- 提出澄清问题
- 建议描述改进
- 帮助格式化指令

### 适用人群

特别适合**前几个 Skill** 的创建。

---

## 四、描述编写最佳实践

### DO（推荐）

- 使用具体动词（extract, create, merge）
- 提供具体用例（form filling, batch operations）
- 设置清晰边界（Not for simple viewing）
- 从 Claude 视角编写

### DON'T（避免）

- 模糊描述（"helps with PDFs"）
- 过于宽泛的范围
- 缺少边界说明

---

## 五、指令编写最佳实践

### 结构化原则

```markdown
# 清晰的层次结构
## Overview
## Prerequisites
## Execution Steps
### Phase 1: Input
### Phase 2: Processing
### Phase 3: Output
## Examples
## Error Handling
## Limitations
```

### 可操作性原则

- 使用代码块展示示例
- 使用项目符号列出选项
- 明确每个阶段的输入和输出

---

## 六、文件大小管理

### "菜单"方法

如果 Skill 覆盖多个不同的流程或选项：

1. **SKILL.md** 描述可用选项
2. 使用**相对路径**引用单独文件
3. Claude 只读取与当前任务相关的文件

**示例结构：**
```
skills/
└── document-processing/
    ├── SKILL.md          # 菜单：描述可用工作流
    ├── pdf-extraction.md # PDF 提取详情
    ├── pdf-creation.md   # PDF 创建详情
    └── pdf-merging.md    # PDF 合并详情
```

### 关键原则

- 将内容拆分为合理的块
- 让 Claude 根据任务选择需要的部分
- 避免每次加载不必要的内容，膨胀上下文窗口

---

## 七、持续迭代

### 监控清单

- [ ] 触发是否一致？
- [ ] 输出是否稳定？
- [ ] 用户是否成功使用？
- [ ] 是否有未覆盖的用例？

### 优化循环

```
部署 → 监控使用 → 发现问题 → 优化描述/指令 → 重新部署
```
