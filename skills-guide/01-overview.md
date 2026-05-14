# Claude Skills 创建指南 - 概览

> 原文：https://claude.com/blog/how-to-create-skills-key-steps-limitations-and-examples
> 发布日期：2025年11月19日
> 阅读时间：约5分钟
> 整理日期：2026-05-14

---

## 什么是 Skills

**Skills（技能）** 是自定义指令，用于扩展 Claude 在特定任务或领域的能力。通过创建 `SKILL.md` 文件，你可以教会 Claude 如何更有效地处理特定场景。

### Skills 的核心价值

1. **编码机构知识** - 将团队的最佳实践和领域知识固化为可复用的指令
2. **标准化输出** - 确保 Claude 在特定任务上输出一致、高质量的结果
3. **处理复杂工作流** - 将多步骤复杂流程编码为自动化技能，避免重复解释

### Skills 的本质

Skills 将 Claude 从**通用助手**转变为**特定工作流的专业专家**。无需投入资源构建自定义 Agent，即可实现专业化的 AI 能力。

---

## 创建 Skills 的两种方式

| 方式 | 说明 | 适用场景 |
|------|------|----------|
| **Skill Creator 模板** | 使用官方提供的模板引导创建 | 初学者、快速上手 |
| **手动编写** | 直接编写 SKILL.md 文件 | 有经验的用户、精细控制 |

### 推荐工具

- **Skill Creator 模板**: [GitHub - anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator)
- **Skills 仓库**: [GitHub - anthropics/skills](https://github.com/anthropics/skills)

---

## 文档索引

- [01-overview.md](./01-overview.md) - 概览（本文档）
- [02-five-steps.md](./02-five-steps.md) - 五步创建法详解
- [03-testing.md](./03-testing.md) - 测试与验证方法
- [04-best-practices.md](./04-best-practices.md) - 最佳实践
- [05-limitations.md](./05-limitations.md) - 限制与注意事项
- [06-examples.md](./06-examples.md) - 真实案例解析
- [07-deployment.md](./07-deployment.md) - 部署与上传指南
