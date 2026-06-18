# ComfyUI 启动流程与 Web 服务分析

## 1. 启动入口 `main.py`

`main.py` 是 ComfyUI 的启动入口，主要职责：
1. 解析命令行参数
2. 配置日志、信号处理、设备环境变量
3. 加载自定义节点预启动脚本
4. 初始化 `PromptServer` 并启动事件循环

### 1.1 启动时序

```python
# main.py
import comfy.options
comfy.options.enable_args_parsing()        # 启用 CLI 参数解析
from comfy.cli_args import args             # 全局参数对象

setup_logger(...)                          # 初始化日志

# 仅在 __main__ 时执行的环境变量设置
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
faulthandler.enable(...)                   # 崩溃时打印 traceback

# 设备相关环境变量
if args.cuda_device is not None:
    os.environ['CUDA_VISIBLE_DEVICES'] = ...

import cuda_malloc                         # CUDA 内存分配优化

execute_prestartup_script()                # 执行 custom_nodes/*/prestartup_script.py
apply_custom_paths()                       # 应用 extra_model_paths.yaml、--output-directory 等

# 启动 PromptServer
server = server.PromptServer(loop)
server.add_routes()                        # 注册路由
loop.run_until_complete(server.run(...))
```

### 1.2 关键 CLI 参数

| 参数 | 作用 |
|------|------|
| `--listen` / `--port` | 绑定地址与端口 |
| `--cpu` | 强制 CPU 推理 |
| `--gpu-only` / `--highvram` / `--normalvram` / `--lowvram` / `--novram` | 显存模式 |
| `--disable-xformers` / `--use-pytorch-cross-attention` | Attention 后端选择 |
| `--output-directory` / `--input-directory` / `--user-directory` | 目录配置 |
| `--extra-model-paths-config` | 额外模型路径配置 |
| `--enable-manager` | 启用 comfyui-manager |
| `--front-end-version` | 指定前端版本 |
| `--disable-all-custom-nodes` / `--whitelist-custom-nodes` | 自定义节点开关 |

这些参数集中在 `comfy/cli_args.py`，通过 `args` 全局对象被各模块读取。

### 1.3 自定义节点预启动

```python
def execute_prestartup_script():
    node_paths = folder_paths.get_folder_paths("custom_nodes")
    for custom_node_path in node_paths:
        for module in os.listdir(custom_node_path):
            script_path = os.path.join(module_path, "prestartup_script.py")
            if os.path.exists(script_path):
                # 动态导入并执行
                spec = importlib.util.spec_from_file_location(module_name, script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
```

这允许自定义节点在 ComfyUI 主逻辑启动前执行安装、依赖检查等操作。

## 2. Web 服务层 `server.py`

`server.py` 定义 `PromptServer` 类，基于 `aiohttp` 提供 HTTP + WebSocket 服务。

### 2.1 PromptServer 初始化

```python
class PromptServer():
    def __init__(self, loop):
        PromptServer.instance = self
        self.user_manager = UserManager()
        self.model_file_manager = ModelFileManager()
        self.custom_node_manager = CustomNodeManager()
        self.subgraph_manager = SubgraphManager()
        self.node_replace_manager = NodeReplaceManager()
        self.internal_routes = InternalRoutes(self)
        self.prompt_queue = execution.PromptQueue(self)
        self.messages = asyncio.Queue()
        self.sockets = dict()
        self.web_root = FrontendManager.init_frontend(...)
        self.app = web.Application(middlewares=middlewares)
```

核心组件：
- `prompt_queue`：工作流执行队列。
- `sockets`：WebSocket 连接池，用于向前端推送进度。
- `web_root`：前端静态资源目录，由 `FrontendManager` 管理。
- `app`：aiohttp 应用实例，挂载路由与中间件。

### 2.2 中间件

| 中间件 | 功能 |
|--------|------|
| `cache_control` | 静态资源缓存控制 |
| `deprecation_warning` | 对 `/scripts/ui` 等旧路径发出弃用警告 |
| `compress_body` | 对 JSON/text 响应启用 gzip（可选） |
| `create_cors_middleware` | 跨域支持（开发模式） |
| `create_origin_only_middleware` | 默认安全策略：校验 Host/Origin，防止跨站请求伪造 |
| `create_block_external_middleware` | 禁用 API 节点时加强 CSP |

### 2.3 核心路由

`PromptServer.add_routes()` 注册了大量路由，主要包括：

| 路由 | 作用 |
|------|------|
| `POST /prompt` | 提交工作流 prompt |
| `POST /queue` | 队列操作（删除、清空） |
| `POST /interrupt` | 中断当前执行 |
| `POST /history` | 清空历史 |
| `GET /queue` | 获取当前队列状态 |
| `GET /history` | 获取执行历史 |
| `GET /object_info` | 获取所有节点元数据（类型、输入、输出） |
| `GET /object_info/{node_class}` | 获取指定节点元数据 |
| `GET /view` | 查看图片/资源 |
| `POST /upload/image` | 上传图片 |
| `GET /system_stats` | 获取系统/硬件信息 |
| `GET /embeddings` | 获取可用 embeddings |
| `GET /models` | 获取模型文件列表 |
| WebSocket `/ws` | 实时推送执行进度、日志、节点预览 |

### 2.4 WebSocket 通信

```python
async def websocket_handler(self, request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    self.sockets[sid] = ws
    # 向前端发送节点树、队列状态
    await self.send("status", {...})
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            data = json.loads(msg.data)
            # 处理客户端消息：prompt、queue、interrupt 等
```

事件类型定义在 `protocol.py`（`BinaryEventTypes`）以及文本消息 `type` 字段中。

### 2.5 Prompt 提交流程

```
POST /prompt
    │
    ▼
PromptQueue.put()
    │
    ▼
execution.PromptExecutor.execute()
    │
    ▼
按拓扑序执行节点
    │
    ▼
通过 WebSocket 发送 status/executing/executed/progress 事件
```

`PromptQueue` 维护待执行队列，支持多 prompt 排队、优先级与历史记录。

## 3. 版本与前端管理

- `comfyui_version.py` 提供当前版本号。
- `app/frontend_management.py` 负责下载、缓存、切换前端版本。
- 通过 `--front-end-version` 可指定本地或远程前端构建产物。

## 4. 安全设计

- **Origin 校验**：默认中间件阻止跨站 POST 到 `127.0.0.1`。
- **CSP**：`create_block_external_middleware` 限制外部资源加载。
- **系统用户隔离**：`folder_paths.py` 中 `__` 前缀用户目录不可通过 HTTP 访问。
- **上传大小限制**：`--max-upload-size` 限制最大上传体积。
