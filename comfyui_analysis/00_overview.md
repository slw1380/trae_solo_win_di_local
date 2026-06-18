# ComfyUI 源码整体架构概览

> 分析对象：ComfyUI 官方仓库（`comfyanonymous/ComfyUI`）
> 分析版本：基于最新 `master` 浅克隆（depth=1）
> 分析时间：2026-06-18

## 1. 项目定位

ComfyUI 是一个基于节点式（node-based）工作流的 Stable Diffusion / 生成式 AI 推理与创作界面。用户通过浏览器拖拽节点、连接边的方式定义图像/视频生成流程；后端用 Python（PyTorch）执行图计算，前端为 React/Vue 构建的 Web 应用。

核心特点：
- **节点化**：一切操作都是节点，输入/输出通过强类型端口连接。
- **图执行引擎**：将前端 JSON 描述的工作流转换为有向无环图（DAG），按拓扑序执行。
- **内存优化**：针对大模型推理做了多级缓存、VRAM 管理、低显存模式。
- **可扩展**：通过 `custom_nodes` 机制支持第三方插件。

## 2. 目录结构总览

```
ComfyUI/
├── main.py                 # 启动入口
├── server.py               # aiohttp Web 服务 / PromptServer
├── execution.py            # 高层执行器与 PromptQueue
├── nodes.py                # 内置节点定义（CLIP、VAE、Latent、Image 等）
├── folder_paths.py         # 模型目录与路径管理
├── comfy/                  # 核心扩散/模型基础设施（~99k 行）
│   ├── model_management.py # 设备、VRAM、CPU/GPU 状态管理
│   ├── sample.py           # 采样入口封装
│   ├── samplers.py         # 采样器与调度器实现
│   ├── sd.py               # CLIP / VAE / UNet / checkpoint 加载
│   ├── model_base.py       # 各模型架构基类（SD、SDXL、Flux、Wan 等）
│   ├── ldm/                # 各扩散模型架构实现
│   └── text_encoders/      # 文本编码器适配
├── comfy_execution/        # 图执行引擎（拓扑排序、缓存、验证）
│   ├── graph.py            # DAG、拓扑排序、ExecutionList
│   ├── caching.py          # 多级缓存策略
│   └── validation.py       # 输入校验
├── app/                    # 新 App 层（用户、模型、前端、资产管理）
│   ├── model_manager.py
│   ├── custom_node_manager.py
│   ├── user_manager.py
│   └── assets/             # 资产生命周期管理
├── comfy_api/              # 内部/外部 API 版本化接口
├── comfy_api_nodes/        # 云端/第三方 API 节点（~46k 行）
├── comfy_extras/           # 扩展节点与工具模型
└── tests-unit/             # 单元测试
```

## 3. 核心数据流

```
用户前端
   │  1. 提交 Prompt（JSON 工作流）
   ▼
PromptServer (server.py)
   │  2. 入队
   ▼
PromptQueue → execution.py
   │  3. 解析为 DynamicPrompt / ExecutionList
   ▼
comfy_execution/graph.py
   │  4. 拓扑排序、依赖解析、缓存命中判断
   ▼
nodes.py / custom_nodes
   │  5. 调用节点 FUNCTION（如 KSampler、CLIPTextEncode）
   ▼
comfy.sample / comfy.samplers / comfy.sd
   │  6. 加载模型、采样、VAE 解码
   ▼
comfy.model_management
   │  7. 设备切换、VRAM 卸载、内存回收
   ▼
输出文件 / WebSocket 进度回传
```

## 4. 关键设计模式

| 模式 | 说明 | 代表文件 |
|------|------|----------|
| 节点注册表 | 运行时发现并注册节点类 | `nodes.py`, `comfy/comfy_types/node_typing.py` |
| 图执行器 | DAG 拓扑排序 + 缓存 + 异步执行 | `comfy_execution/graph.py`, `execution.py` |
| 模型补丁 | `ModelPatcher` 包装原始模型，支持 LoRA、ControlNet、量化 | `comfy/model_patcher.py` |
| 内存状态机 | `VRAMState` / `CPUState` 枚举驱动加载/卸载策略 | `comfy/model_management.py` |
| 类型系统 | `IO` 枚举定义端口类型，`INPUT_TYPES()` 声明节点参数 | `comfy/comfy_types/__init__.py` |

## 5. 架构演进观察

- **传统核心**：`main.py` + `server.py` + `execution.py` + `nodes.py` + `comfy/` 是早期主体。
- **执行引擎重构**：`comfy_execution/` 从 `execution.py` 中拆分，提供更清晰的 DAG、缓存、验证层。
- **新 App 层**：`app/` 引入现代应用架构（用户管理、模型文件管理、前端版本管理、资产管理）。
- **API 节点化**：`comfy_api_nodes/` 将外部 SaaS API 封装为普通节点，统一工作流体验。
- **版本化 API**：`comfy_api/latest/`, `comfy_api/v0_0_1/` 等支持节点 API 向后兼容。

## 6. 后续文档索引

| 文档 | 内容 |
|------|------|
| `01_entry_and_server.md` | 启动流程、CLI 参数、PromptServer、WebSocket、REST API |
| `02_execution_engine.md` | 图执行引擎、拓扑排序、缓存策略、ExecutionList |
| `03_node_system.md` | 节点类型系统、内置节点、节点注册机制 |
| `04_model_management.md` | 模型加载、VRAM/CPU 状态、内存优化、ModelPatcher |
| `05_sampling_and_diffusion.md` | 采样器、调度器、条件处理、模型架构抽象 |
| `06_custom_nodes_and_api.md` | 自定义节点生命周期、API 节点、扩展机制 |
| `07_app_layer.md` | 新 App 层：用户、模型、前端、资产管理 |
| `08_code_statistics.md` | 代码量统计、模块分布、核心文件清单 |
