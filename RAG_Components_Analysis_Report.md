# RAG 组件分析报告

**——开源技术栈全景图**

*2026年5月12日*

---

## 一、RAG 概述

### 1.1 什么是 RAG

**RAG = Retrieval-Augmented Generation**（检索增强生成），这是一种将外部知识检索与大语言模型生成结合的技术架构，让 AI 能够基于私有/专业文档回答问题。

### 1.2 RAG 工作流程

RAG 系统包含两个主要阶段：

**数据索引阶段：**
```
文档 → Loader（加载） → Splitter（分块） → Embedding（向量化） → Vector Store（存储）
```

**查询阶段：**
```
用户问题 → Embedding（向量化） → Retriever（检索） → Prompt（组装） → LLM（生成回答）
```

### 1.3 核心价值

解决 LLM 的三大痛点：

- 知识时效性：可接入实时数据
- 私有知识：支持企业内部文档
- 幻觉问题：基于事实检索生成

---

## 二、核心组件详解

### 2.1 文档加载器 (Document Loaders)

| 工具 | 支持格式 | 说明 |
|------|----------|------|
| PyMuPDF | PDF | 高性能 PDF 解析 |
| pypdf | PDF | 轻量级 PDF 处理 |
| marker-pdf | PDF | 先进解析（含表格、公式） |
| surya-ocr | PDF/图片 | OCR 识别 |
| python-docx | Word | Word 文档解析 |
| trafilatura | 网页 | 网页内容提取 |
| Unstructured | 多格式 | 通用文档解析 |

### 2.2 文本分割器 (Text Splitters)

| 工具 | 特点 |
|------|------|
| RecursiveCharacterTextSplitter | LangChain 内置，递归分割，通用性最强 |
| SemanticTextSplitter | 基于语义的分割，保持语义完整性 |
| SpacyTextSplitter | 基于 NER 的分割 |
| NLTKTextSplitter | 基于句子的分割 |
| TiktokenTextSplitter | 基于 Token 的分割 |

### 2.3 嵌入模型 (Embeddings)

#### 2.3.1 开源 Embedding 模型

| 模型 | 特点 | 开源 |
|------|------|------|
| BGE (BAAI) | 国产最强，支持多语言 | 是 |
| M3E (MokaAI) | 中文优化 | 是 |
| Sentence-BERT | 通用句向量 | 是 |
| GTE (华为) | 多语言支持 | 是 |

#### 2.3.2 使用示例

```python
from sentence_transformers import SentenceTransformer

# BGE (推荐)
model = SentenceTransformer('BAAI/bge-large-zh-v1.5')

# M3E
model = SentenceTransformer('moka-ai/m3e-base')
```

### 2.4 向量数据库 (Vector Stores)

| 数据库 | 特点 | 部署方式 |
|--------|------|----------|
| Chroma | 轻量、嵌入式、学习友好 | 本地/服务器 |
| FAISS | Facebook 高性能 | 本地 |
| Milvus | 分布式、生产级 | Docker/K8s |
| Qdrant | Rust 实现、高性能 | Docker |
| Weaviate | 混合检索 | Docker/K8s |
| Pinecone | 云托管 | 云服务 |
| pgvector | PostgreSQL 扩展 | 自托管 |
| Neo4j | 图数据库+向量 | Docker |
| Elasticsearch | 8.x+ 支持向量 | 自托管 |

**选型建议：**

- 开发测试：Chroma / FAISS
- 生产环境：Milvus / Qdrant
- 企业级：Weaviate / Elasticsearch
- 已有 PostgreSQL：pgvector

### 2.5 检索器 (Retrievers)

| 类型 | 说明 |
|------|------|
| 向量检索 | Top-K 相似度检索 |
| 混合检索 | 关键词 + 向量组合 |
| 重排序 (Reranker) | Cross-Encoder 优化结果 |
| BM25 | 传统关键词检索 |
| 知识图谱检索 | Graph RAG |

**常用 Reranker 模型：**

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder('BAAI/bge-reranker-large')
```

### 2.6 LLM（大语言模型）

| 模型 | 开源 | 说明 |
|------|------|------|
| Llama 3 | 是 | Meta 开源 |
| Qwen | 是 | 阿里开源，中文能力强 |
| DeepSeek | 是 | 国产高性能 |
| Mistral | 是 | 欧洲开源 |
| GPT-4 | 否 | OpenAI 闭源 |
| Claude | 否 | Anthropic 闭源 |

**本地部署工具：**

- Ollama：简单的本地模型运行工具
- vLLM：高性能推理服务
- LM Studio：桌面应用

---

## 三、RAG 框架对比

| 框架 | 定位 | 特点 |
|------|------|------|
| LangChain | 全功能框架 | 组件丰富，学习曲线陡 |
| LlamaIndex | 数据框架 | RAG 专精 |
| RAGFlow | 开箱即用 | 可视化，深度文档理解 |
| LightRAG | 轻量快速 | 知识图谱集成 |
| UltraRAG | 多模态 | MCP 架构，清华出品 |
| Dify | 无代码平台 | 可视化编排 |
| MaxKB | 智能问答 | 开源 RAG 应用 |

---

## 四、推荐技术栈组合

### 4.1 轻量开发版

**适用场景：个人学习、快速原型**

- PDF: PyMuPDF
- 分块: RecursiveCharacterTextSplitter
- 嵌入: BGE / M3E
- 向量库: Chroma / FAISS
- LLM: Ollama (本地) / DeepSeek API
- 框架: LangChain / LlamaIndex

### 4.2 生产环境版

**适用场景：企业级应用、中等规模部署**

- 文档解析: marker-pdf
- 分块: 自定义语义分块
- 嵌入: BGE-large-zh
- 向量库: Milvus / Qdrant
- Reranker: BAAI/bge-reranker
- LLM: Qwen / DeepSeek (API)
- 框架: LangGraph + LlamaIndex

### 4.3 企业级版

**适用场景：大规模生产、高可用要求**

- 文档解析: Unstructured
- 嵌入: OpenAI Embedding / Cohere
- 向量库: Pinecone / Weaviate
- 检索: 混合检索 + Reranker
- LLM: GPT-4 / Claude
- 框架: LangGraph + LangChain

---

## 五、RAG vs 微调 vs 预训练

| 方法 | 成本 | 时效性 | 准确性 | 适用场景 |
|------|------|--------|--------|----------|
| RAG | 低 | 高 | 中高 | 动态知识、实时数据 |
| 微调 | 中 | 低 | 高 | 领域适配、风格迁移 |
| 预训练 | 高 | 无 | 中 | 通用知识 |

---

## 六、总结

RAG 是 LLM 应用的基础技术，通过结合外部知识检索与 LLM 生成，解决知识时效性、私有知识利用和幻觉问题。

| 组件 | 开源推荐 |
|------|----------|
| 文档解析 | PyMuPDF, marker-pdf |
| 文本分割 | LangChain Splitters |
| 嵌入模型 | BGE, M3E, GTE |
| 向量数据库 | Chroma, FAISS, Milvus |
| 检索器 | 混合检索 + Reranker |
| LLM | Qwen, DeepSeek, Llama |

---

*报告生成时间：2026年5月12日*
