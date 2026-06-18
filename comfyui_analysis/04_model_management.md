# ComfyUI 模型管理与内存优化分析

ComfyUI 需要加载大量生成式 AI 模型（SD checkpoint、LoRA、VAE、CLIP、ControlNet 等），模型管理与内存优化是其核心能力之一。

## 1. 设备与显存状态

### 1.1 状态枚举

`comfy/model_management.py` 定义全局状态：

```python
class VRAMState(Enum):
    DISABLED = 0    # 无显存
    NO_VRAM = 1     # 极低显存
    LOW_VRAM = 2
    NORMAL_VRAM = 3
    HIGH_VRAM = 4
    SHARED = 5      # 共享内存（如 Apple Silicon / iGPU）

class CPUState(Enum):
    GPU = 0
    CPU = 1
    MPS = 2         # Apple Metal
```

### 1.2 自动检测

启动时根据平台和 PyTorch 后端自动检测：

```python
try:
    if torch.backends.mps.is_available():
        cpu_state = CPUState.MPS
except:
    pass

# 检测 CUDA / XPU / NPU / MLU 等
```

CLI 参数 `--cpu`、 `--highvram`、 `--lowvram` 等会覆盖默认状态。

## 2. 设备抽象

### 2.1 get_torch_device

```python
def get_torch_device():
    if directml_enabled:
        return directml_device
    if cpu_state == CPUState.MPS:
        return torch.device("mps")
    if cpu_state == CPUState.CPU:
        return torch.device("cpu")
    # 多后端 GPU 支持
    if is_intel_xpu(): return torch.device("xpu", ...)
    if is_ascend_npu(): return torch.device("npu", ...)
    if is_mlu(): return torch.device("mlu", ...)
    return torch.device(torch.cuda.current_device())
```

ComfyUI 通过统一函数屏蔽 NVIDIA / AMD / Intel / Apple / 昇腾 / 寒武纪等后端差异。

## 3. 模型加载与卸载

### 3.1 load_models_gpu / load_model_gpu

```python
def load_models_gpu(models, force_patch_weights=False, force_full_load=False):
    # 计算需要的显存
    # 尝试加载模型到 GPU
    # 如果显存不足，按 VRAM 策略部分卸载或移动到 CPU
```

### 3.2 卸载策略

根据 `VRAMState` 选择加载策略：

| 模式 | 行为 |
|------|------|
| HIGH_VRAM | 尽量常驻 GPU，减少切换 |
| NORMAL_VRAM | 运行时加载，用完后保留部分 |
| LOW_VRAM | 仅加载当前计算需要的部分 |
| NO_VRAM | 大量卸载到 CPU/磁盘 |
| SHARED | 模型与内存共享，特殊处理 |

### 3.3 unload_all_models

```python
def unload_all_models():
    # 将所有已加载模型移回 CPU 或释放
```

## 4. ModelPatcher 模型补丁

`comfy/model_patcher.py` 是 ComfyUI 模型增强的核心抽象。

### 4.1 职责

- 包装原始 `torch.nn.Module`。
- 管理模型所在设备（CPU/GPU）。
- 支持 LoRA、ControlNet、Hook、量化等 patch。
- 实现模型权重的前向/后向 patch 应用。

### 4.2 关键接口

```python
class ModelPatcher:
    def __init__(self, model, load_device, offload_device, size=0, ...):
        self.model = model
        self.load_device = load_device
        self.offload_device = offload_device
        self.patches = {}

    def add_patches(self, patches, strength_patch=1.0, strength_model=1.0):
        # 注册权重 patch（如 LoRA）

    def patch_model(self, device_to=None, patch_weights=True):
        # 将 patch 应用到模型权重

    def unpatch_model(self, device_to=None, unpatch_weights=True):
        # 还原原始权重
```

### 4.3 LoRA 应用流程

```
checkpoint -> ModelPatcher
    │
    ▼
LoraLoader 加载 LoRA weights
    │
    ▼
add_patches() 注册 patch
    │
    ▼
patch_model() 在推理前应用
    │
    ▼
推理
    │
    ▼
unpatch_model() 还原（可选，取决于模式）
```

## 5. 内存管理细节

### 5.1 中间设备

```python
def intermediate_device():
    # 返回存放中间张量的设备（通常是 CPU 或 GPU）
```

采样后的 latent 通常会移回 `intermediate_device()`，避免占用 GPU 显存。

### 5.2 确定性算法

`--deterministic` 启用 PyTorch 确定性算法，保证结果可复现。

### 5.3 量化支持

`comfy/quant_ops.py` 封装多种量化操作，支持 INT8/FP8/INT4 等推理加速。

## 6. 模型目录管理

`folder_paths.py` 集中管理模型搜索路径：

```python
folder_names_and_paths["checkpoints"] = ([os.path.join(models_dir, "checkpoints")], supported_pt_extensions)
folder_names_and_paths["loras"] = ([os.path.join(models_dir, "loras")], supported_pt_extensions)
folder_names_and_paths["vae"] = ([os.path.join(models_dir, "vae")], supported_pt_extensions)
# ...
```

通过 `add_model_folder_path()` 允许自定义节点或配置扩展路径。

## 7. 多 GPU 支持

`comfy/multigpu.py` 与 `model_management.py` 中的 `get_all_torch_devices()` 提供多 GPU 支持：

- `--cuda-device` 指定主 GPU。
- 模型可在多个设备间分配（实验性）。
- `multigpu` 相关节点允许用户在工作流中指定设备。

## 8. 优化总结

| 优化点 | 实现 |
|--------|------|
| 显存分级 | VRAMState 枚举 + 对应加载策略 |
| 按需加载 | 仅将当前计算所需模型/层移入 GPU |
| 权重 patch | ModelPatcher 支持 LoRA/ControlNet 等动态 patch |
| 中间张量回传 | 采样结果返回 intermediate_device |
| 量化加速 | quant_ops 支持多种低精度推理 |
| 多后端兼容 | 统一 get_torch_device 抽象 CUDA/XPU/NPU/MLU/MPS |
