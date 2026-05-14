# Claude Skills 创建指南 - 部署与上传

---

## 部署平台概览

| 平台 | 适用场景 | 管理方式 | 计划要求 |
|------|----------|----------|----------|
| **Claude.ai** | 个人使用、Claude Apps | 用户个人设置 | Pro/Max/Team/Enterprise |
| **Claude Code** | 项目级、团队协作 | 项目目录自动发现 | 无特定要求 |
| **Developer Platform** | 程序化、企业集成 | API 管理 | API 访问权限 |

---

## 平台一：Claude.ai（Claude Apps）

### 部署步骤

1. 登录 [Claude.ai](https://claude.ai)
2. 进入 **Settings**
3. 找到自定义 Skill 设置
4. 上传 SKILL.md 文件

### 限制与注意事项

- **个人级别**：Skill 属于单个用户
- **不组织共享**：无法由管理员集中管理
- **计划要求**：需要 Pro、Max、Team 或 Enterprise
- **代码执行**：需要启用代码执行功能

### 适用场景

- 个人工作流优化
- 快速原型验证
- 不依赖特定项目的通用 Skill

---

## 平台二：Claude Code

### 目录结构

```
my-project/
├── src/
├── tests/
├── skills/                    # Skill 目录
│   └── my-skill/             # Skill 文件夹
│       └── SKILL.md          # Skill 定义文件
│       └── additional-ref.md # 可选：附加参考文件
├── README.md
└── pyproject.toml
```

### 自动发现机制

- Claude Code 安装插件后自动发现 `skills/` 目录
- 根据 `name` 和 `description` 决定触发时机
- 无需手动注册

### 项目级 Skill 优势

- **团队共享**：项目成员共享同一套 Skill
- **版本控制**：Skill 随项目代码一起版本管理
- **上下文感知**：Skill 了解项目特定约定

### 适用场景

- 项目特定的工作流
- 团队标准化
- 编码规范执行

---

## 平台三：Claude Developer Platform（API）

### API 端点

```
POST https://api.anthropic.com/v1/skills
```

### 请求示例

```bash
curl -X POST "https://api.anthropic.com/v1/skills" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: skills-2025-10-02" \
  -F "display_title=My Skill Name" \
  -F "files[]=@my-skill/SKILL.md;filename=my-skill/SKILL.md"
```

### 必需 Header

| Header | 值 | 说明 |
|--------|-----|------|
| `x-api-key` | `$ANTHROPIC_API_KEY` | API 认证 |
| `anthropic-version` | `2023-06-01` | API 版本 |
| `anthropic-beta` | `skills-2025-10-02` | Beta 功能标识 |

### 请求参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `display_title` | string | Skill 显示名称 |
| `files[]` | file | SKILL.md 文件（可包含多个） |

### 适用场景

- 程序化部署
- 企业级管理
- CI/CD 集成
- 大规模 Skill 分发

---

## 部署检查清单

### 部署前

- [ ] 已完成三步测试（正常/边界/越界）
- [ ] 描述准确反映 Skill 能力
- [ ] 指令结构化且可操作
- [ ] 已说明限制和边界
- [ ] 文件大小合理（使用菜单方法）

### 部署后

- [ ] 验证 Skill 能被正确触发
- [ ] 测试典型用例输出质量
- [ ] 监控实际使用情况
- [ ] 收集用户反馈
- [ ] 准备迭代优化

---

## 多平台部署策略

### 策略一：从 Claude Code 开始

```
1. 在项目中创建 skills/ 目录
2. 与团队一起迭代优化
3. 成熟后考虑发布到 Claude.ai 或 API
```

### 策略二：个人到团队

```
1. 在 Claude.ai 上创建个人 Skill
2. 验证有效性
3. 迁移到项目级（Claude Code）
4. 团队共享使用
```

### 策略三：企业级管理

```
1. 通过 API 统一部署
2. 集中管理和版本控制
3. 组织级共享和权限控制
```

---

## 版本管理建议

### Skill 版本控制

```
skills/
└── my-skill/
    ├── v1/
    │   └── SKILL.md
    ├── v2/
    │   └── SKILL.md
    └── current -> v2/  # 符号链接到当前版本
```

### 变更日志

在 Skill 目录中维护 CHANGELOG.md：

```markdown
# My Skill Changelog

## v2.0.0
- 新增：支持批量处理
- 优化：触发描述更准确

## v1.0.0
- 初始版本
- 支持基本功能
```
