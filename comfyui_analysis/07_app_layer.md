# ComfyUI 新 App 层分析

ComfyUI 在传统核心之外，新增了 `app/` 目录，引入更现代的应用层架构，负责用户、模型、前端、资产等管理。

## 1. App 层定位

`app/` 层是 ComfyUI 向完整应用平台演进的表现：

- **用户管理**：多用户、系统用户隔离。
- **模型管理**：模型文件索引、元数据、下载。
- **前端管理**：前端版本下载与切换。
- **资产管理**：输入/输出/生成的文件作为资产持久化。
- **自定义节点管理**：安装、启用、禁用、更新。

## 2. 模块结构

```
app/
├── __init__.py
├── app_settings.py          # 应用配置
├── logger.py                # 日志初始化
├── user_manager.py          # 用户管理
├── model_manager.py         # 模型文件管理
├── custom_node_manager.py   # 自定义节点管理
├── frontend_management.py   # 前端版本管理
├── node_replace_manager.py  # 节点替换映射
├── subgraph_manager.py      # 子图管理
├── database/
│   ├── db.py                # SQLAlchemy 数据库
│   └── models.py            # ORM 模型
└── assets/
    ├── scanner.py           # 资产扫描
    ├── seeder.py            # 资产种子
    ├── helpers.py           # 资产辅助
    └── api/                 # 资产 REST API
```

## 3. 用户管理

### 3.1 UserManager

`app/user_manager.py` 管理用户目录与权限。

核心功能：
- 创建用户目录
- 区分 Public User 与 System User
- 为 HTTP 请求解析 user_id

### 3.2 系统用户隔离

`folder_paths.py` 中定义：

```python
SYSTEM_USER_PREFIX = "__"

def get_system_user_directory(name: str = "system") -> str:
    # 返回 __system 等目录

def get_public_user_directory(user_id: str) -> str | None:
    # 对 __ 前缀用户返回 None，禁止 HTTP 访问
```

这是重要的安全设计，防止内部数据通过 `/view` 等接口泄露。

## 4. 模型管理

### 4.1 ModelFileManager

`app/model_manager.py` 提供模型文件管理：

- 扫描 `folder_paths` 中注册的模型目录。
- 提供模型列表、搜索、元数据。
- 与前端 `/models` 接口对接。

### 4.2 与 folder_paths 的关系

`folder_paths.py` 仍是底层路径注册中心，`ModelFileManager` 在其之上提供应用级抽象。

## 5. 前端管理

### 5.1 FrontendManager

`app/frontend_management.py` 负责前端构建产物的下载、缓存、版本切换。

```python
class FrontendManager:
    @staticmethod
    def init_frontend(version):
        # 下载或定位指定版本前端
        # 返回 web_root 路径
```

### 5.2 版本解析

```python
def parse_version(version_str):
    # 解析 "latest" / "v1.x.x" / 本地路径
```

## 6. 资产管理

### 6.1 资产概念

ComfyUI 将图片、视频、音频等文件抽象为 Asset，存入数据库并管理其生命周期。

### 6.2 核心组件

| 组件 | 职责 |
|------|------|
| `app/assets/seeder.py` | 启动时扫描已有文件，生成资产记录 |
| `app/assets/scanner.py` | 监控目录变化 |
| `app/assets/helpers.py` | 资产元数据、hash 计算 |
| `app/assets/api/routes.py` | 注册资产 REST API |

### 6.3 数据库

`app/database/db.py` 使用 SQLAlchemy + Alembic 迁移：

```
alembic_db/versions/
├── 0001_assets.py
├── 0002_merge_to_asset_references.py
├── 0003_add_metadata_job_id.py
└── 0004_drop_tag_type.py
```

## 7. 子图与节点替换

### 7.1 SubgraphManager

`app/subgraph_manager.py` 管理工作流中的子图（subgraph）节点，支持嵌套工作流。

### 7.2 NodeReplaceManager

`app/node_replace_manager.py` 处理节点替换映射，例如工作流中使用了旧节点名时自动映射到新节点。

## 8. 日志

`app/logger.py` 初始化结构化日志：

```python
def setup_logger(log_level="INFO", use_stdout=False):
    # 配置 logging，支持 stdout 与文件
```

## 9. App 层与传统层交互

```
server.py PromptServer
    │
    ├── UserManager        <- 用户目录与权限
    ├── ModelFileManager   <- 模型文件列表
    ├── CustomNodeManager  <- 自定义节点管理
    ├── SubgraphManager    <- 子图
    ├── NodeReplaceManager <- 节点兼容性
    └── InternalRoutes     <- 内部 API
```

## 10. 总结

| 模块 | 作用 |
|------|------|
| `user_manager.py` | 多用户与系统用户隔离 |
| `model_manager.py` | 应用级模型文件管理 |
| `frontend_management.py` | 前端版本生命周期 |
| `custom_node_manager.py` | 插件管理 |
| `assets/` | 文件资产化与数据库持久化 |
| `database/` | ORM 与迁移 |

`app/` 层的引入让 ComfyUI 从单一推理工具向可运营、可管理的平台演进。
