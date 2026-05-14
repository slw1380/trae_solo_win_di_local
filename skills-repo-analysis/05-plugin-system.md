# Claude Code 插件系统

---

## 插件市场

Anthropic Skills 仓库可作为 Claude Code 的**插件市场**使用。

### 注册插件市场

```bash
/plugin marketplace add anthropics/skills
```

### 安装插件步骤

1. 选择 `Browse and install plugins`
2. 选择 `anthropic-agent-skills`
3. 选择 `document-skills` 或 `example-skills`
4. 选择 `Install now`

### 直接安装命令

```bash
# 安装文档处理 Skills
/plugin install document-skills@anthropic-agent-skills

# 安装示例 Skills
/plugin install example-skills@anthropic-agent-skills
```

---

## 插件使用

安装后，通过自然语言调用 Skill：

```bash
"Use the PDF skill to extract the form fields from path/to/some-file.pdf"
```

Claude 自动识别并加载对应的 Skill。

---

## 插件配置

### .claude-plugin 目录

仓库根目录包含 `.claude-plugin/` 目录，用于配置 Claude Code 插件：

```
.claude-plugin/
└── ...  # 插件配置文件
```

### 插件发现机制

1. Claude Code 扫描已注册的插件市场
2. 发现 `skills/` 目录下的 Skill 集合
3. 根据 `name` 和 `description` 建立索引
4. 用户请求时匹配并加载相关 Skill

---

## 插件 vs 本地 Skills

| 特性 | 插件市场安装 | 本地 skills/ 目录 |
|------|-------------|------------------|
| **安装方式** | `/plugin install` | 手动创建目录 |
| **来源** | 远程仓库 | 本地项目 |
| **更新** | 跟随仓库更新 | 手动维护 |
| **共享** | 团队统一版本 | 项目特定 |
| **适用场景** | 通用 Skills | 项目特定 Skills |

---

## 自定义插件市场

任何 GitHub 仓库都可以注册为插件市场，只要包含：
- `skills/` 目录
- 每个 Skill 独立的子目录
- 每个子目录包含 `SKILL.md`

### 注册自定义市场

```bash
/plugin marketplace add your-org/your-skills-repo
```

---

## 插件系统架构

```
┌─────────────────────────────────────┐
│           Claude Code                │
│  ┌─────────────────────────────┐    │
│  │      Plugin Manager          │    │
│  │  - Marketplace registry      │    │
│  │  - Skill discovery           │    │
│  │  - Version management        │    │
│  └─────────────┬───────────────┘    │
│                │                     │
│  ┌─────────────▼───────────────┐    │
│  │      Skill Index             │    │
│  │  - name + description        │    │
│  │  - Loaded at startup         │    │
│  └─────────────┬───────────────┘    │
│                │                     │
│  ┌─────────────▼───────────────┐    │
│  │      Skill Loader            │    │
│  │  - Match request to skill    │    │
│  │  - Load SKILL.md on demand   │    │
│  │  - Load references as needed │    │
│  └─────────────────────────────┘    │
└─────────────────────────────────────┘
```
