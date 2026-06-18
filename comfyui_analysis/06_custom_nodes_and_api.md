# ComfyUI 自定义节点与 API 扩展分析

ComfyUI 的强大之处在于其扩展性。本章分析自定义节点生命周期、第三方 API 节点封装机制。

## 1. 自定义节点机制

### 1.1 目录结构

自定义节点位于 `ComfyUI/custom_nodes/`，每个子目录/文件是一个插件包：

```
custom_nodes/
├── my_custom_nodes/
│   ├── __init__.py
│   ├── nodes.py
│   └── prestartup_script.py   # 预启动脚本
└── another_node.py
```

### 1.2 加载流程

启动时 `main.py` / `nodes.py` 执行：

```python
def load_custom_node(module_path, module_key=None):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    # 收集 NODE_CLASS_MAPPINGS 与 NODE_DISPLAY_NAME_MAPPINGS
```

### 1.3 最小自定义节点示例

```python
# custom_nodes/example_node.py
class MyNode:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"value": ("INT", {"default": 1, "min": 0, "max": 100})}}
    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"
    CATEGORY = "custom"

    def execute(self, value):
        return (value * 2,)

NODE_CLASS_MAPPINGS = {"MyNode": MyNode}
NODE_DISPLAY_NAME_MAPPINGS = {"MyNode": "My Custom Node"}
```

### 1.4 预启动脚本

`prestartup_script.py` 在 ComfyUI 主模块导入前执行，常用于：
- 安装缺失依赖
- 修改 sys.path
- 下载模型
- 注册自定义包

## 2. 自定义节点管理器

`app/custom_node_manager.py` 提供对自定义节点的管理功能：

- 列出已安装节点
- 启用/禁用节点
- 检测节点冲突
- 与 comfyui-manager 集成（如果启用）

## 3. 版本化节点 API

### 3.1 为什么需要版本化

随着 ComfyUI 迭代，节点 API 也在演进。`comfy_api/` 提供版本化接口，保证旧节点继续工作。

### 3.2 API 版本

```
comfy_api/
├── v0_0_1/          # 早期 API
├── v0_0_2/
├── latest/          # 当前推荐 API
│   ├── io.py        # V3 输入/输出类型
│   ├── _io.py       # 内部辅助
│   └── _ui.py
└── internal/        # 内部节点基类与工具
    ├── api_registry.py
    └── singleton.py
```

### 3.3 V3 节点基类

```python
from comfy_api.latest import io, ComfyExtension, InputImpl
from comfy_api.internal import _ComfyNodeInternal

class MyV3Node(_ComfyNodeInternal):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {...},
            "hidden": { "unique_id": io.Hidden.unique_id }
        }

    @classmethod
    def fingerprint_inputs(cls, **kwargs):
        # 替代 IS_CHANGED
        return "fingerprint"
```

## 4. API 节点（Cloud API Nodes）

`comfy_api_nodes/` 将外部云服务商 API 封装为本地节点。

### 4.1 架构

```
comfy_api_nodes/
├── apis/              # 各服务商 API 客户端
│   ├── openai.py
│   ├── gemini.py
│   ├── stability.py
│   └── ...
├── util/              # 公共工具
│   ├── client.py      # HTTP client 封装
│   ├── upload_helpers.py
│   ├── download_helpers.py
│   └── validation_utils.py
└── nodes_*.py         # 对应节点定义
```

### 4.2 统一 Client

```python
# util/client.py
class ComfyAPIClient:
    async def post(self, url, data, headers=None):
        # aiohttp 请求，带重试、日志
```

### 4.3 OpenAI 节点示例

`nodes_openai.py` 可能包含：
- `OpenAIDalleImageGenerate`：文生图
- `OpenAIDalleImageEdit`：图像编辑
- `OpenAIGPTImageGenerate`：GPT-4o 图像生成

这些节点处理 API key、上传输入图、下载结果图，并返回 `IMAGE` 类型输出。

### 4.4 安全性

- API key 通常通过环境变量或隐藏输入传递。
- `--disable-api-nodes` 可完全禁用 API 节点。
- `create_block_external_middleware` 加强 CSP。

## 5. 前端扩展

前端也支持扩展：
- 自定义节点可以通过注册前端脚本扩展 UI。
- `ComfyExtension` 类允许节点提供前端扩展元数据。

## 6. 扩展示意图

```
ComfyUI 核心
    │
    ├── custom_nodes/          第三方插件
    │      └── 直接注册节点
    │
    ├── comfy_extras/          官方扩展节点
    │      └── 与核心一起发布
    │
    ├── comfy_api_nodes/       云端 API 节点
    │      └── 外部服务接入
    │
    └── app/custom_node_manager 管理扩展
```

## 7. 扩展开发建议

| 建议 | 说明 |
|------|------|
| 使用 ComfyNodeABC | 继承官方基类，兼容类型系统 |
| 明确 INPUT_TYPES | 避免类型错误和前端渲染异常 |
| 合理使用 IS_CHANGED / fingerprint_inputs | 影响缓存与重算 |
| 避免在模块顶层加载大模型 | 应延迟到节点执行时加载 |
| 使用 folder_paths | 统一模型路径管理 |
| 处理异常 | 提供清晰错误信息 |
