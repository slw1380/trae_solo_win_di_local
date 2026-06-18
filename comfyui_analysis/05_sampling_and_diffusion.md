# ComfyUI 采样器与扩散模型分析

本章聚焦 ComfyUI 如何封装 PyTorch 扩散模型、实现采样调度、处理条件（conditioning）。

## 1. 扩散模型抽象

### 1.1 BaseModel

`comfy/model_base.py` 定义 `BaseModel`，是所有具体模型架构的基类：

```python
class BaseModel(torch.nn.Module):
    def __init__(self, model_config, model_type=ModelType.EPS, device=None):
        super().__init__()
        self.diffusion_model = ...
        self.model_type = model_type
        self.model_config = model_config
        # ...

    def apply_model(self, x, t, c_concat=None, c_crossattn=None, ...):
        # 前向传播，被子类重写
```

`BaseModel` 之上派生出大量具体架构：

- SD 1.x / SD 2.x
- SDXL / SDXL Refiner / SDXL_instructpix2pix
- SD3 / Flux / Flux2 / Chroma / Lumina2
- HunyuanVideo / LTXV / Wan2.1 / Wan2.2
- CogVideoX / Cosmos / Mochi
- Stable Audio / Hunyuan3D / SAM3 / RT-DETR

### 1.2 ModelConfig

`model_config` 包含：
- `unet_config`：网络结构参数。
- `latent_format`：latent 空间格式（通道数、下采样率）。
- `model_sampling`：噪声调度参数（beta、sigma 范围等）。

## 2. 模型加载

### 2.1 Checkpoint 加载

`comfy/sd.py` 提供：

```python
def load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, ...):
    # 读取 safetensors / ckpt
    # 自动识别模型类型
    # 返回 model, clip, vae, clip_vision
```

### 2.2 模型识别

`comfy/model_detection.py` 与 `comfy/supported_models.py` 通过 state_dict 的 key 和形状自动判断模型架构：

```python
def model_detection_error_hint(path, state_dict):
    # 识别失败时给出提示
```

### 2.3 Diffusion Model 单独加载

```python
def load_diffusion_model(unet_path, model_options={}, disable_dynamic=False):
    # 加载 UNet / DiT 权重
```

## 3. 文本编码与条件

### 3.1 CLIP 类

`comfy/sd.py` 中 `CLIP` 类封装文本编码器：

```python
class CLIP:
    def tokenize(self, text):
        # 分词
    def encode_from_tokens_scheduled(self, tokens):
        # 编码为 conditioning
```

### 3.2 Conditioning 结构

Conditioning 是一个列表，每个元素为 `[tensor, dict]`：

```python
[
  [cond_tensor, {"pooled_output": pooled, "crossattn": crossattn}],
  ...
]
```

`nodes.py` 中的 `ConditioningCombine`、`ConditioningAverage`、`ConditioningSetMask` 等节点用于编辑 conditioning。

### 3.3 条件批处理

`comfy/samplers.py` 中 `calc_cond_batch` 实现正负条件的批量计算：

```python
def calc_cond_batch(model, conds, x_in, timestep, model_options):
    # 合并可拼接的条件，减少模型前向次数
```

这是 ComfyUI 相比 naive 实现的重要性能优化。

## 4. 采样器

### 4.1 KSampler

`comfy/samplers.py` 中 `KSampler` 类是用户最常用的采样器封装：

```python
class KSampler:
    def __init__(self, model, steps, device, sampler, scheduler, ...):
        self.model = model
        self.model_sampling = model.get_model_object("model_sampling")
        self.set_steps(steps, denoise)
        self.set_sampler(sampler)
```

### 4.2 采样函数

```python
def sample(model, noise, positive, negative, cfg, device, sampler, sigmas,
           model_options={}, latent_image=None, denoise_mask=None, ...):
    # 实际采样入口
```

### 4.3 调度器

`comfy/samplers.py` 提供多种 sigma 调度：

```python
def simple_scheduler(model_sampling, steps):
def ddim_scheduler(model_sampling, steps):
def normal_scheduler(model_sampling, steps, sgm=False, floor=False):
def beta_scheduler(model_sampling, steps, alpha=0.6, beta=0.6):
def linear_quadratic_schedule(...):
def kl_optimal_scheduler(n, sigma_min, sigma_max):
```

通过 `calculate_sigmas()` 统一调用。

### 4.4 采样算法

`comfy/k_diffusion/sampling.py` 提供基于 k-diffusion 的算法：

- Euler
- Euler a
- Heun
- DPM++ 2M / 2M Karras
- DPM2 / DPM2 a
- LMS
- DDIM
- UniPC

`comfy/samplers.py` 通过 `ksampler()` 工厂函数创建对应采样器对象。

## 5. 高级采样特性

### 5.1 CFG（Classifier-Free Guidance）

`CFGGuider` 实现标准 CFG：

```python
class CFGGuider:
    def predict_noise(self, x, timestep, model_options={}, seed=None):
        # 分别计算 cond 和 uncond
        # 按 cfg 缩放
```

### 5.2 Inpainting

`KSamplerX0Inpaint` 处理局部重绘，通过 `denoise_mask` 只修改指定区域。

### 5.3 Hooks

`comfy/hooks.py` 允许在采样过程中注入自定义行为（如自定义 attention 修改、风格控制）。

### 5.4 ControlNet

`comfy/controlnet.py` 实现 ControlNet 条件注入：

```python
class ControlBase:
    def copy(self):
    def get_control(self, x_noisy, t, cond, batched_number):
```

ControlNet 在 `calc_cond_batch` 期间将控制信号合并进 conditioning。

## 6. VAE 编解码

`comfy/sd.py` 中 `VAE` 类：

```python
class VAE:
    def encode(self, pixel_samples):
        # 像素空间 -> latent 空间
    def decode(self, samples_in):
        # latent 空间 -> 像素空间
```

支持 tiled VAE（大图分块编解码，降低显存占用）。

## 7. 采样流程总结

```
KSampler 节点
    │
    ▼
comfy.sample.sample()
    │
    ▼
KSampler.sample()
    │
    ▼
计算 sigmas（scheduler）
    │
    ▼
采样器迭代（k-diffusion）
    │  每一步调用 model_function
    ▼
CFG / conditioning / ControlNet 合并
    │
    ▼
模型前向（BaseModel.apply_model）
    │
    ▼
输出 samples
    │
    ▼
VAEDecode -> 图像
```

## 8. 代码分布

| 文件 | 职责 |
|------|------|
| `comfy/model_base.py` | 模型架构基类 |
| `comfy/ldm/` | 各模型具体实现 |
| `comfy/sd.py` | CLIP / VAE / checkpoint 加载 |
| `comfy/sample.py` | 采样入口封装 |
| `comfy/samplers.py` | 采样器、调度器、CFG |
| `comfy/k_diffusion/` | k-diffusion 采样算法 |
| `comfy/controlnet.py` | ControlNet 注入 |
| `comfy/lora.py` | LoRA 加载与应用 |
