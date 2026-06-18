# ComfyUI 节点系统分析

ComfyUI 的所有功能都通过节点暴露。本章分析节点类型系统、内置节点组织、节点注册与发现机制。

## 1. 节点类型系统

### 1.1 IO 类型定义

`comfy/comfy_types/__init__.py` 定义了核心端口类型枚举 `IO`：

```python
class IO(str, Enum):
    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    LATENT = "LATENT"
    IMAGE = "IMAGE"
    MASK = "MASK"
    MODEL = "MODEL"
    CLIP = "CLIP"
    VAE = "VAE"
    CONDITIONING = "CONDITIONING"
    GLIGEN = "GLIGEN"
    UPSCALE_MODEL = "UPSCALE_MODEL"
    # ... 更多类型
```

这些字符串同时作为前端端口类型和后端校验类型。

### 1.2 节点基类

```python
class ComfyNodeABC(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        pass

    RETURN_TYPES: tuple[str, ...]
    RETURN_NAMES: tuple[str, ...] = ()
    FUNCTION: str
    CATEGORY: str = ""
    DESCRIPTION: str = ""
    OUTPUT_NODE: bool = False
    INPUT_IS_LIST: bool = False
    OUTPUT_IS_LIST: tuple[bool, ...] = ()
    # ...
```

每个节点类必须实现：
- `INPUT_TYPES()`：声明输入参数（required/optional/hidden）。
- `RETURN_TYPES`：声明输出端口类型。
- `FUNCTION`：指定实际执行业务逻辑的方法名。

### 1.3 输入声明示例

```python
class CLIPTextEncode(ComfyNodeABC):
    @classmethod
    def INPUT_TYPES(s) -> InputTypeDict:
        return {
            "required": {
                "text": (IO.STRING, {"multiline": True, "dynamicPrompts": True}),
                "clip": (IO.CLIP, {})
            }
        }
    RETURN_TYPES = (IO.CONDITIONING,)
    FUNCTION = "encode"
    CATEGORY = "model/conditioning"

    def encode(self, clip, text):
        tokens = clip.tokenize(text)
        return (clip.encode_from_tokens_scheduled(tokens), )
```

### 1.4 输入选项

常见输入选项：

| 选项 | 说明 |
|------|------|
| `default` | 默认值 |
| `min` / `max` / `step` | 数值范围与步长 |
| `multiline` | 文本框多行 |
| `dynamicPrompts` | 支持动态提示词语法 |
| `lazy` | 懒加载输入 |
| `rawLink` | 接收原始链接而非解析后的值 |
| `tooltip` | 悬浮提示 |
| `forceInput` | 强制显示为输入端口 |

## 2. 内置节点组织

### 2.1 `nodes.py` 核心节点

`nodes.py`（约 2500 行）包含最基础、最常用的节点：

| 类别 | 代表节点 |
|------|----------|
| Conditioning | `CLIPTextEncode`, `ConditioningCombine`, `ConditioningAverage`, `ConditioningSetMask`, `ConditioningSetArea` |
| Latent | `EmptyLatentImage`, `VAEEncode`, `VAEDecode`, `LatentUpscale`, `LatentCrop`, `LatentFromBatch` |
| Image | `LoadImage`, `SaveImage`, `PreviewImage`, `ImageScale`, `ImageCrop`, `ImageBatch`, `ImageCompositeMasked` |
| Mask | `MaskFromImage`, `ImageToMask`, `MaskComposite`, `MaskToImage` |
| Model | `CheckpointLoaderSimple`, `UNETLoader`, `CLIPLoader`, `VAELoader`, `LoraLoader`, `ControlNetLoader` |
| Sampler | `KSampler`, `KSamplerAdvanced` |
| Advanced | `ModelSamplingDiscrete`, `SetLatentNoiseMask`, `SDTurboScheduler` |

### 2.2 `comfy_extras/` 扩展节点

`comfy_extras/` 包含大量非核心但常用的节点：

- `nodes_advanced_samplers.py`：高级采样器
- `nodes_flux.py`：Flux 模型相关节点
- `nodes_video.py` / `nodes_video_model.py`：视频生成节点
- `nodes_controlnet.py`：ControlNet 扩展
- `nodes_lora_*.py`：LoRA 工具
- `nodes_mask.py` / `nodes_images.py`：图像与掩码处理
- `nodes_mediapipe.py`：MediaPipe 集成

### 2.3 `comfy_api_nodes/` API 节点

将外部 SaaS API 封装为 ComfyUI 节点，例如：

- `nodes_openai.py`：OpenAI DALL-E / GPT 图像编辑
- `nodes_gemini.py`：Google Gemini
- `nodes_stability.py`：Stability AI
- `nodes_kling.py` / `nodes_luma.py` / `nodes_runway.py`：国内/国外视频 API

这些节点通过统一 client 调用 REST API，并处理上传/下载/验证。

## 3. 节点注册机制

### 3.1 注册表

运行时，ComfyUI 维护以下全局注册表：

```python
NODE_CLASS_MAPPINGS = {}       # class_type -> node_class
NODE_DISPLAY_NAME_MAPPINGS = {} # class_type -> display_name
```

### 3.2 注册过程

1. `nodes.py` 自身定义并注册核心节点。
2. `comfy_extras` 中的模块通过 `NODE_CLASS_MAPPINGS[name] = Class` 注册。
3. `custom_nodes` 中的第三方包通过 `__init__.py` 或 `NODE_CLASS_MAPPINGS` 注册。

注册工具函数：

```python
def load_custom_node(module_path, module_key=None):
    # 动态导入模块
    # 提取 NODE_CLASS_MAPPINGS / NODE_DISPLAY_NAME_MAPPINGS
    # 合并到全局注册表
```

### 3.3 显示名称映射

`NODE_DISPLAY_NAME_MAPPINGS` 允许节点类使用内部名称，同时给前端展示友好名称。

```python
NODE_DISPLAY_NAME_MAPPINGS["CLIPTextEncode"] = "CLIP Text Encode (Prompt)"
```

## 4. 节点执行约定

### 4.1 返回值

普通节点返回一个元组，长度与 `RETURN_TYPES` 一致：

```python
return (conditioning,)        # 单输出
return (image, mask)          # 多输出
```

### 4.2 UI 反馈

节点可以返回 UI 元数据，例如预览图：

```python
return {"ui": {"images": images}, "result": (image,)}
```

### 4.3 列表输入/输出

- `INPUT_IS_LIST = True`：所有输入作为列表批量处理。
- `OUTPUT_IS_LIST = (True, False)`：指定哪些输出是列表。

### 4.4 输出节点

`OUTPUT_NODE = True` 表示该节点是工作流终点（如 `SaveImage`、`PreviewImage`）。执行引擎会优先将这些节点加入 ExecutionList。

## 5. 节点发现与元数据接口

`GET /object_info` 返回所有注册节点的元数据，前端据此渲染节点面板。

```json
{
  "CLIPTextEncode": {
    "input": { "required": { "text": ["STRING", {"multiline": true}], "clip": ["CLIP", {}] } },
    "output": ["CONDITIONING"],
    "output_name": ["CONDITIONING"],
    "name": "CLIPTextEncode",
    "display_name": "CLIP Text Encode (Prompt)",
    "description": "...",
    "category": "model/conditioning",
    "output_node": false
  }
}
```

## 6. 节点版本化 API（V3 节点）

`comfy_api/latest/io.py` 与 `comfy_api/internal/` 引入更现代的节点 API：

- `_ComfyNodeInternal`：新版节点基类。
- `Hidden` 枚举：提供 `prompt`、`dynprompt`、`extra_pnginfo`、`unique_id` 等隐藏输入。
- `fingerprint_inputs()`：替代 `IS_CHANGED`，用于缓存指纹。

这种设计让节点可以更安全地访问执行上下文，同时保持向后兼容。

## 7. 节点系统总结

| 方面 | 说明 |
|------|------|
| 声明式输入 | 通过 `INPUT_TYPES()` 声明参数类型与 UI 行为 |
| 强类型端口 | `IO` 枚举约束连接关系 |
| 注册表驱动 | 运行时动态发现节点，支持热插拔 |
| 元数据接口 | `/object_info` 让前端零配置渲染节点 |
| 扩展友好 | `custom_nodes` + `comfy_extras` 双轨扩展 |
