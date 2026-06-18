# ComfyUI 代码统计与模块分布

## 1. 总体规模

| 指标 | 数值 |
|------|------|
| Python 文件总数 | 约 650+ |
| Python 代码总行数 | 约 220,000+ |
| 顶层模块数 | 约 25 个 |

> 注：统计基于 `/workspace/ComfyUI` 浅克隆，未包含前端代码（`ComfyUI/web/` 由 FrontendManager 动态拉取）。

## 2. 顶层模块代码量

| 模块/文件 | 文件数 | Python 行数 | 说明 |
|-----------|--------|-------------|------|
| `comfy/` | 263 | 99,253 | 核心扩散/模型基础设施 |
| `comfy_api_nodes/` | 80 | 46,159 | 云端/第三方 API 节点 |
| `comfy_extras/` | 124 | 36,519 | 官方扩展节点与工具 |
| `tests-unit/` | 69 | 14,263 | 单元测试 |
| `app/` | 36 | 9,651 | 新应用层 |
| `comfy_api/` | 36 | 6,144 | 版本化节点 API |
| `tests/` | 22 | 5,470 | 测试脚本 |
| `nodes.py` | 1 | 2,534 | 核心内置节点 |
| `comfy_execution/` | 9 | 2,119 | 图执行引擎 |
| `execution.py` | 1 | 1,380 | 高层执行器 |
| `server.py` | 1 | 1,336 | Web 服务 |
| `main.py` | 1 | 571 | 启动入口 |
| `folder_paths.py` | 1 | 506 | 路径管理 |
| 其他 | ~7 | ~1,500 | 工具脚本、配置等 |

## 3. 核心文件清单

### 3.1 启动与服务

| 文件 | 行数 | 核心职责 |
|------|------|----------|
| `main.py` | 571 | 启动入口、CLI 参数、自定义节点预启动 |
| `server.py` | 1,336 | PromptServer、HTTP/WebSocket 路由、中间件 |
| `execution.py` | 1,380 | PromptExecutor、PromptQueue、节点调用 |
| `folder_paths.py` | 506 | 模型目录、输入输出目录管理 |
| `comfyui_version.py` | 3 | 版本号 |

### 3.2 图执行引擎

| 文件 | 行数 | 核心职责 |
|------|------|----------|
| `comfy_execution/graph.py` | ~700 | DAG、拓扑排序、ExecutionList |
| `comfy_execution/caching.py` | ~430 | HierarchicalCache、LRU、RAMPressureCache |
| `comfy_execution/validation.py` | ~150 | 输入校验 |
| `comfy_execution/progress.py` | ~200 | 进度追踪与 WebSocket 推送 |
| `comfy_execution/asset_enrichment.py` | ~150 | 输出资产增强 |

### 3.3 模型与扩散

| 文件 | 行数 | 核心职责 |
|------|------|----------|
| `comfy/model_management.py` | ~1,200 | 设备、VRAM、加载卸载 |
| `comfy/sd.py` | ~2,100 | CLIP / VAE / checkpoint 加载 |
| `comfy/samplers.py` | ~1,500 | 采样器、调度器、CFG |
| `comfy/sample.py` | 81 | 采样入口封装 |
| `comfy/model_base.py` | ~2,500 | BaseModel 与各模型架构 |
| `comfy/model_patcher.py` | ~800 | 模型补丁、LoRA、ControlNet |
| `comfy/controlnet.py` | ~600 | ControlNet 条件注入 |
| `comfy/lora.py` | ~300 | LoRA 加载 |

### 3.4 模型架构子目录（comfy/ldm/）

`comfy/ldm/` 包含大量具体模型实现，代码量前几：

| 子目录 | 主要职责 |
|--------|----------|
| `flux/` | Flux / Flux2 系列 |
| `wan/` | Wan2.1 / Wan2.2 视频模型 |
| `hunyuan_video/` | 混元视频 |
| `ltxv/` | LTX Video |
| `cosmos/` | Cosmos 视频 |
| `moge/` | MoGe 几何估计 |
| `sam3/` | SAM3 分割 |
| `modules/` | 公共 attention、ema、temporal 模块 |

### 3.5 节点系统

| 文件 | 行数 | 核心职责 |
|------|------|----------|
| `nodes.py` | 2,534 | 核心内置节点 |
| `comfy/comfy_types/__init__.py` | ~100 | IO 类型与 ComfyNodeABC |
| `comfy/comfy_types/node_typing.py` | ~200 | 类型辅助函数 |
| `comfy_extras/` | 36,519 | 官方扩展节点 |
| `comfy_api_nodes/` | 46,159 | API 节点 |

## 4. 代码增长趋势观察

- `comfy_api_nodes/` 以 ~46k 行成为第二大模块，说明 ComfyUI 正在大力发展云端 API 集成。
- `comfy/ldm/` 持续扩张，覆盖 SD、SDXL、SD3、Flux、视频、3D、音频等多模态模型。
- `app/` 层接近 10k 行，显示项目正从工具向平台化演进。
- 单元测试 `tests-unit/` 约 14k 行，覆盖 app、assets、执行等关键路径。

## 5. 代码质量工具

ComfyUI 仓库配置了多种代码质量工具：

| 工具 | 配置 |
|------|------|
| ruff | `.github/workflows/ruff.yml` |
| mypy / 类型检查 | `comfy_types/` 与类型注解 |
| pytest | `pytest.ini` |
| GitHub Actions | `.github/workflows/` 多个 CI 工作流 |

## 6. 统计脚本

如需重新生成统计，可在 ComfyUI 根目录运行：

```python
from pathlib import Path
root = Path('.')
stats = {}
for pyfile in root.rglob('*.py'):
    rel = pyfile.relative_to(root)
    top = rel.parts[0] if rel.parts else ''
    lines = len(pyfile.read_text(errors='ignore').splitlines())
    stats.setdefault(top, {'files': 0, 'lines': 0})
    stats[top]['files'] += 1
    stats[top]['lines'] += lines

for k in sorted(stats, key=lambda x: -stats[x]['lines']):
    print(f"{k}: {stats[k]['files']} files, {stats[k]['lines']} lines")
```
