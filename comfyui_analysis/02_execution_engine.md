# ComfyUI 图执行引擎分析

ComfyUI 的核心竞争力之一是其节点式工作流执行引擎。本章分析 `comfy_execution/` 与 `execution.py` 如何将前端 JSON 工作流转换为可执行的 DAG。

## 1. 核心概念

| 概念 | 说明 |
|------|------|
| **Prompt** | 前端提交的工作流 JSON，每个 key 是一个节点 ID，value 包含 `class_type` 和 `inputs`。 |
| **DynamicPrompt** | 执行期动态图，支持在执行过程中添加临时（ephemeral）节点。 |
| **ExecutionList** | 带缓存意识的拓扑排序执行列表。 |
| **Output Cache** | 节点输出缓存，避免重复计算；支持 Classic、LRU、RAM Pressure、Null 等策略。 |
| **ExecutionBlocker** | 懒加载输入占位符，用于支持 lazy 输入。 |

## 2. 数据结构

### 2.1 Prompt JSON 示例

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": { "ckpt_name": "model.safetensors" }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": { "text": "a beautiful landscape", "clip": ["1", 1] }
  },
  "3": {
    "class_type": "KSampler",
    "inputs": { "model": ["1", 0], "positive": ["2", 0], ... }
  }
}
```

输入链接表示为 `[node_id, output_index]` 的列表。

### 2.2 DynamicPrompt

```python
class DynamicPrompt:
    def __init__(self, original_prompt):
        self.original_prompt = original_prompt
        self.ephemeral_prompt = {}      # 执行期动态添加的节点
        self.ephemeral_parents = {}     # 临时节点到真实节点的映射
        self.ephemeral_display = {}     # 显示 ID 映射

    def get_node(self, node_id):
        # 优先查临时节点，再查原始节点
```

支持子图（subgraph）、循环展开等高级特性。

## 3. 拓扑排序

`comfy_execution/graph.py` 中的 `TopologicalSort` 实现 DAG 拓扑排序。

### 3.1 算法思路

1. 从目标输出节点开始反向遍历（add_node）。
2. 对每个输入链接，建立强依赖（add_strong_link）。
3. 维护 `blockCount`：节点被多少个前置节点阻塞。
4. 当 `blockCount == 0` 时，节点可执行。
5. 节点执行完成后，减少依赖它的节点的 `blockCount`。

```python
def add_strong_link(self, from_node_id, from_socket, to_node_id):
    if not self.is_cached(from_node_id):
        self.add_node(from_node_id)
        if to_node_id not in self.blocking[from_node_id]:
            self.blocking[from_node_id][to_node_id] = {}
            self.blockCount[to_node_id] += 1
        self.blocking[from_node_id][to_node_id][from_socket] = True
```

### 3.2 ExecutionList

`ExecutionList` 继承 `TopologicalSort`，增加了缓存意识：

```python
class ExecutionList(TopologicalSort):
    def __init__(self, dynprompt, output_cache):
        super().__init__(dynprompt)
        self.output_cache = output_cache
        self.execution_cache = {}
        self.execution_cache_listeners = {}

    def is_cached(self, node_id):
        return self.output_cache.get_local(node_id) is not None
```

当节点输出已缓存时，不会加入待执行集合，直接复用结果。

## 4. 执行器 `execution.py`

`PromptExecutor` 是高层执行器，负责：
- 接收 prompt 并创建 `DynamicPrompt`
- 初始化缓存
- 调用 `ExecutionList` 获取可执行节点
- 调用节点函数
- 处理输出、异常、进度

### 4.1 执行主循环

```python
async def execute(self, prompt, prompt_id, extra_data={}, execute_outputs=[]):
    dynprompt = DynamicPrompt(prompt)
    output_cache = CacheSet(...)
    execution_list = ExecutionList(dynprompt, output_cache)

    # 添加输出节点
    for node_id in execute_outputs:
        execution_list.add_node(node_id)

    while not execution_list.is_empty():
        node_id, _, _ = await execution_list.stage_node_execution()
        if node_id is None:
            break

        # 执行节点
        result = await self.execute_node(node_id, dynprompt, output_cache)
        # 缓存结果、通知下游节点
        execution_list.unstage_node_execution()
```

### 4.2 节点执行

```python
async def execute_node(self, node_id, dynprompt, output_cache):
    node = dynprompt.get_node(node_id)
    class_type = node["class_type"]
    class_def = nodes.NODE_CLASS_MAPPINGS[class_type]

    # 收集输入数据
    input_data_all, missing_keys, v3_data = get_input_data(
        node["inputs"], class_def, node_id, execution_list, dynprompt, extra_data
    )

    # 调用节点 FUNCTION
    function_name = class_def.FUNCTION
    output = await _async_map_node_over_list(..., function_name, ...)

    # 处理输出：UI 元数据 + 数据元组
    output_ui = {}
    has_subgraph = False
    if isinstance(output, dict):
        output_ui = output.get("ui", {})
        has_subgraph = output.get("subgraph", False)
        output = output.get("result", [])

    # 写入缓存
    output_cache.set(node_id, CacheEntry(ui=output_ui, outputs=output))
```

## 5. 缓存策略

`comfy_execution/caching.py` 提供多种缓存实现。

### 5.1 缓存类型

```python
class CacheType(Enum):
    CLASSIC = 0      # 默认：输入签名缓存输出，ID 缓存对象
    LRU = 1          # 最近最少使用
    NONE = 2         # 禁用缓存
    RAM_PRESSURE = 3 # 根据 RAM 压力自动回收
```

### 5.2 CacheSet

```python
class CacheSet:
    def __init__(self, cache_type=None, cache_args={}):
        self.outputs = HierarchicalCache(CacheKeySetInputSignature, enable_providers=True)
        self.objects = HierarchicalCache(CacheKeySetID)
```

- `outputs`：基于输入签名的结果缓存。
- `objects`：基于节点 ID 的对象缓存（如模型实例）。

### 5.3 HierarchicalCache

支持分层缓存（本地缓存 + 外部 provider），允许自定义节点扩展缓存来源。

### 5.4 IS_CHANGED 机制

节点可定义 `IS_CHANGED` 类方法，返回一个指纹。当输入未变但 `IS_CHANGED` 返回变化时，节点会重新执行。

```python
@classmethod
def IS_CHANGED(s, ...):
    return float("NaN")  # 永远变化
```

## 6. 懒加载输入

节点输入可以声明为 `lazy=True`。懒输入不会强制前置节点先执行，节点内部可通过特殊机制请求值。

```python
"inputs": {
    "optional": {
        "optional_input": ("LATENT", {"lazy": True})
    }
}
```

`ExecutionBlocker` 用于表示尚未计算的输入。

## 7. 验证与错误处理

`comfy_execution/validation.py` 在节点执行前校验输入类型、链接有效性。

常见错误：
- `DependencyCycleError`：工作流存在循环依赖。
- `NodeInputError`：输入类型不匹配或缺失。
- `NodeNotFoundError`：引用了不存在的节点。

## 8. 执行流程总结

```
Prompt JSON
    │
    ▼
DynamicPrompt
    │
    ▼
ExecutionList (拓扑排序 + 缓存命中判断)
    │
    ▼
stage_node_execution() → 返回就绪节点
    │
    ▼
get_input_data() 收集输入（从缓存或上游输出）
    │
    ▼
调用节点 FUNCTION
    │
    ▼
输出写入 CacheSet
    │
    ▼
unstage_node_execution() 释放依赖阻塞
    │
    ▼
循环直到所有节点执行完毕
```
