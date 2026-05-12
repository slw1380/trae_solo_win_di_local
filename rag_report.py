from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT

doc = Document()

doc.add_heading('RAG 组件分析报告', 0)
doc.add_paragraph('——开源技术栈全景图')

doc.add_paragraph('2026年5月12日')
doc.add_paragraph('')

doc.add_heading('一、RAG 概述', level=1)

doc.add_heading('1.1 什么是 RAG', level=2)
p = doc.add_paragraph()
p.add_run('RAG = Retrieval-Augmented Generation').bold = True
p.add_run('（检索增强生成），这是一种将外部知识检索与大语言模型生成结合的技术架构，让 AI 能够基于私有/专业文档回答问题。')

doc.add_heading('1.2 RAG 工作流程', level=2)
doc.add_paragraph('RAG 系统包含两个主要阶段：')

doc.add_paragraph('数据索引阶段：')
doc.add_paragraph('文档 → Loader（加载） → Splitter（分块） → Embedding（向量化） → Vector Store（存储）', style='List Bullet')

doc.add_paragraph('查询阶段：')
doc.add_paragraph('用户问题 → Embedding（向量化） → Retriever（检索） → Prompt（组装） → LLM（生成回答）', style='List Bullet')

doc.add_heading('1.3 核心价值', level=2)
doc.add_paragraph('解决 LLM 的三大痛点：', style='List Bullet')
doc.add_paragraph('知识时效性：可接入实时数据', style='List Bullet')
doc.add_paragraph('私有知识：支持企业内部文档', style='List Bullet')
doc.add_paragraph('幻觉问题：基于事实检索生成', style='List Bullet')

doc.add_heading('二、核心组件详解', level=1)

doc.add_heading('2.1 文档加载器 (Document Loaders)', level=2)

loader_table = doc.add_table(rows=8, cols=3)
loader_table.style = 'Table Grid'
cells = loader_table.rows[0].cells
cells[0].text = '工具'
cells[1].text = '支持格式'
cells[2].text = '说明'
cells = loader_table.rows[1].cells
cells[0].text = 'PyMuPDF'
cells[1].text = 'PDF'
cells[2].text = '高性能 PDF 解析'
cells = loader_table.rows[2].cells
cells[0].text = 'pypdf'
cells[1].text = 'PDF'
cells[2].text = '轻量级 PDF 处理'
cells = loader_table.rows[3].cells
cells[0].text = 'marker-pdf'
cells[1].text = 'PDF'
cells[2].text = '先进解析（含表格、公式）'
cells = loader_table.rows[4].cells
cells[0].text = 'surya-ocr'
cells[1].text = 'PDF/图片'
cells[2].text = 'OCR 识别'
cells = loader_table.rows[5].cells
cells[0].text = 'python-docx'
cells[1].text = 'Word'
cells[2].text = 'Word 文档解析'
cells = loader_table.rows[6].cells
cells[0].text = 'trafilatura'
cells[1].text = '网页'
cells[2].text = '网页内容提取'
cells = loader_table.rows[7].cells
cells[0].text = 'Unstructured'
cells[1].text = '多格式'
cells[2].text = '通用文档解析'

doc.add_heading('2.2 文本分割器 (Text Splitters)', level=2)

splitter_table = doc.add_table(rows=6, cols=2)
splitter_table.style = 'Table Grid'
cells = splitter_table.rows[0].cells
cells[0].text = '工具'
cells[1].text = '特点'
cells = splitter_table.rows[1].cells
cells[0].text = 'RecursiveCharacterTextSplitter'
cells[1].text = 'LangChain 内置，递归分割，通用性最强'
cells = splitter_table.rows[2].cells
cells[0].text = 'SemanticTextSplitter'
cells[1].text = '基于语义的分割，保持语义完整性'
cells = splitter_table.rows[3].cells
cells[0].text = 'SpacyTextSplitter'
cells[1].text = '基于 NER 的分割'
cells = splitter_table.rows[4].cells
cells[0].text = 'NLTKTextSplitter'
cells[1].text = '基于句子的分割'
cells = splitter_table.rows[5].cells
cells[0].text = 'TiktokenTextSplitter'
cells[1].text = '基于 Token 的分割'

doc.add_heading('2.3 嵌入模型 (Embeddings)', level=2)

doc.add_paragraph('2.3.1 开源 Embedding 模型')
embed_table = doc.add_table(rows=5, cols=3)
embed_table.style = 'Table Grid'
cells = embed_table.rows[0].cells
cells[0].text = '模型'
cells[1].text = '特点'
cells[2].text = '开源'
cells = embed_table.rows[1].cells
cells[0].text = 'BGE (BAAI)'
cells[1].text = '国产最强，支持多语言'
cells[2].text = '是'
cells = embed_table.rows[2].cells
cells[0].text = 'M3E (MokaAI)'
cells[1].text = '中文优化'
cells[2].text = '是'
cells = embed_table.rows[3].cells
cells[0].text = 'Sentence-BERT'
cells[1].text = '通用句向量'
cells[2].text = '是'
cells = embed_table.rows[4].cells
cells[0].text = 'GTE (华为)'
cells[1].text = '多语言支持'
cells[2].text = '是'

doc.add_paragraph('')
doc.add_paragraph('2.3.2 使用示例')
code_para = doc.add_paragraph()
code_para.add_run('from sentence_transformers import SentenceTransformer\n').italic = True
code_para.add_run('# BGE (推荐)\n').italic = True
code_para.add_run('model = SentenceTransformer(\'BAAI/bge-large-zh-v1.5\')\n\n').italic = True
code_para.add_run('# M3E\n').italic = True
code_para.add_run('model = SentenceTransformer(\'moka-ai/m3e-base\')').italic = True

doc.add_heading('2.4 向量数据库 (Vector Stores)', level=2)

vector_table = doc.add_table(rows=10, cols=3)
vector_table.style = 'Table Grid'
cells = vector_table.rows[0].cells
cells[0].text = '数据库'
cells[1].text = '特点'
cells[2].text = '部署方式'
cells = vector_table.rows[1].cells
cells[0].text = 'Chroma'
cells[1].text = '轻量、嵌入式、学习友好'
cells[2].text = '本地/服务器'
cells = vector_table.rows[2].cells
cells[0].text = 'FAISS'
cells[1].text = 'Facebook 高性能'
cells[2].text = '本地'
cells = vector_table.rows[3].cells
cells[0].text = 'Milvus'
cells[1].text = '分布式、生产级'
cells[2].text = 'Docker/K8s'
cells = vector_table.rows[4].cells
cells[0].text = 'Qdrant'
cells[1].text = 'Rust 实现、高性能'
cells[2].text = 'Docker'
cells = vector_table.rows[5].cells
cells[0].text = 'Weaviate'
cells[1].text = '混合检索'
cells[2].text = 'Docker/K8s'
cells = vector_table.rows[6].cells
cells[0].text = 'Pinecone'
cells[1].text = '云托管'
cells[2].text = '云服务'
cells = vector_table.rows[7].cells
cells[0].text = 'pgvector'
cells[1].text = 'PostgreSQL 扩展'
cells[2].text = '自托管'
cells = vector_table.rows[8].cells
cells[0].text = 'Neo4j'
cells[1].text = '图数据库+向量'
cells[2].text = 'Docker'
cells = vector_table.rows[9].cells
cells[0].text = 'Elasticsearch'
cells[1].text = '8.x+ 支持向量'
cells[2].text = '自托管'

doc.add_paragraph('')
doc.add_paragraph('选型建议：')
doc.add_paragraph('开发测试：Chroma / FAISS', style='List Bullet')
doc.add_paragraph('生产环境：Milvus / Qdrant', style='List Bullet')
doc.add_paragraph('企业级：Weaviate / Elasticsearch', style='List Bullet')
doc.add_paragraph('已有 PostgreSQL：pgvector', style='List Bullet')

doc.add_heading('2.5 检索器 (Retrievers)', level=2)

retriever_table = doc.add_table(rows=6, cols=2)
retriever_table.style = 'Table Grid'
cells = retriever_table.rows[0].cells
cells[0].text = '类型'
cells[1].text = '说明'
cells = retriever_table.rows[1].cells
cells[0].text = '向量检索'
cells[1].text = 'Top-K 相似度检索'
cells = retriever_table.rows[2].cells
cells[0].text = '混合检索'
cells[1].text = '关键词 + 向量组合'
cells = retriever_table.rows[3].cells
cells[0].text = '重排序 (Reranker)'
cells[1].text = 'Cross-Encoder 优化结果'
cells = retriever_table.rows[4].cells
cells[0].text = 'BM25'
cells[1].text = '传统关键词检索'
cells = retriever_table.rows[5].cells
cells[0].text = '知识图谱检索'
cells[1].text = 'Graph RAG'

doc.add_paragraph('')
doc.add_paragraph('常用 Reranker 模型：')
reranker_para = doc.add_paragraph()
reranker_para.add_run('from sentence_transformers import CrossEncoder\n').italic = True
reranker_para.add_run('model = CrossEncoder(\'BAAI/bge-reranker-large\')').italic = True

doc.add_heading('2.6 LLM（大语言模型）', level=2)

llm_table = doc.add_table(rows=7, cols=3)
llm_table.style = 'Table Grid'
cells = llm_table.rows[0].cells
cells[0].text = '模型'
cells[1].text = '开源'
cells[2].text = '说明'
cells = llm_table.rows[1].cells
cells[0].text = 'Llama 3'
cells[1].text = '是'
cells[2].text = 'Meta 开源'
cells = llm_table.rows[2].cells
cells[0].text = 'Qwen'
cells[1].text = '是'
cells[2].text = '阿里开源，中文能力强'
cells = llm_table.rows[3].cells
cells[0].text = 'DeepSeek'
cells[1].text = '是'
cells[2].text = '国产高性能'
cells = llm_table.rows[4].cells
cells[0].text = 'Mistral'
cells[1].text = '是'
cells[2].text = '欧洲开源'
cells = llm_table.rows[5].cells
cells[0].text = 'GPT-4'
cells[1].text = '否'
cells[2].text = 'OpenAI 闭源'
cells = llm_table.rows[6].cells
cells[0].text = 'Claude'
cells[1].text = '否'
cells[2].text = 'Anthropic 闭源'

doc.add_paragraph('')
doc.add_paragraph('本地部署工具：')
doc.add_paragraph('Ollama：简单的本地模型运行工具', style='List Bullet')
doc.add_paragraph('vLLM：高性能推理服务', style='List Bullet')
doc.add_paragraph('LM Studio：桌面应用', style='List Bullet')

doc.add_heading('三、RAG 框架对比', level=1)

framework_table = doc.add_table(rows=8, cols=3)
framework_table.style = 'Table Grid'
cells = framework_table.rows[0].cells
cells[0].text = '框架'
cells[1].text = '定位'
cells[2].text = '特点'
cells = framework_table.rows[1].cells
cells[0].text = 'LangChain'
cells[1].text = '全功能框架'
cells[2].text = '组件丰富，学习曲线陡'
cells = framework_table.rows[2].cells
cells[0].text = 'LlamaIndex'
cells[1].text = '数据框架'
cells[2].text = 'RAG 专精'
cells = framework_table.rows[3].cells
cells[0].text = 'RAGFlow'
cells[1].text = '开箱即用'
cells[2].text = '可视化，深度文档理解'
cells = framework_table.rows[4].cells
cells[0].text = 'LightRAG'
cells[1].text = '轻量快速'
cells[2].text = '知识图谱集成'
cells = framework_table.rows[5].cells
cells[0].text = 'UltraRAG'
cells[1].text = '多模态'
cells[2].text = 'MCP 架构，清华出品'
cells = framework_table.rows[6].cells
cells[0].text = 'Dify'
cells[1].text = '无代码平台'
cells[2].text = '可视化编排'
cells = framework_table.rows[7].cells
cells[0].text = 'MaxKB'
cells[1].text = '智能问答'
cells[2].text = '开源 RAG 应用'

doc.add_heading('四、推荐技术栈组合', level=1)

doc.add_heading('4.1 轻量开发版', level=2)
doc.add_paragraph('适用场景：个人学习、快速原型')
doc.add_paragraph('PDF: PyMuPDF', style='List Bullet')
doc.add_paragraph('分块: RecursiveCharacterTextSplitter', style='List Bullet')
doc.add_paragraph('嵌入: BGE / M3E', style='List Bullet')
doc.add_paragraph('向量库: Chroma / FAISS', style='List Bullet')
doc.add_paragraph('LLM: Ollama (本地) / DeepSeek API', style='List Bullet')
doc.add_paragraph('框架: LangChain / LlamaIndex', style='List Bullet')

doc.add_heading('4.2 生产环境版', level=2)
doc.add_paragraph('适用场景：企业级应用、中等规模部署')
doc.add_paragraph('文档解析: marker-pdf', style='List Bullet')
doc.add_paragraph('分块: 自定义语义分块', style='List Bullet')
doc.add_paragraph('嵌入: BGE-large-zh', style='List Bullet')
doc.add_paragraph('向量库: Milvus / Qdrant', style='List Bullet')
doc.add_paragraph('Reranker: BAAI/bge-reranker', style='List Bullet')
doc.add_paragraph('LLM: Qwen / DeepSeek (API)', style='List Bullet')
doc.add_paragraph('框架: LangGraph + LlamaIndex', style='List Bullet')

doc.add_heading('4.3 企业级版', level=2)
doc.add_paragraph('适用场景：大规模生产、高可用要求')
doc.add_paragraph('文档解析: Unstructured', style='List Bullet')
doc.add_paragraph('嵌入: OpenAI Embedding / Cohere', style='List Bullet')
doc.add_paragraph('向量库: Pinecone / Weaviate', style='List Bullet')
doc.add_paragraph('检索: 混合检索 + Reranker', style='List Bullet')
doc.add_paragraph('LLM: GPT-4 / Claude', style='List Bullet')
doc.add_paragraph('框架: LangGraph + LangChain', style='List Bullet')

doc.add_heading('五、RAG vs 微调 vs 预训练', level=1)

compare_table = doc.add_table(rows=4, cols=5)
compare_table.style = 'Table Grid'
cells = compare_table.rows[0].cells
cells[0].text = '方法'
cells[1].text = '成本'
cells[2].text = '时效性'
cells[3].text = '准确性'
cells[4].text = '适用场景'
cells = compare_table.rows[1].cells
cells[0].text = 'RAG'
cells[1].text = '低'
cells[2].text = '高'
cells[3].text = '中高'
cells[4].text = '动态知识、实时数据'
cells = compare_table.rows[2].cells
cells[0].text = '微调'
cells[1].text = '中'
cells[2].text = '低'
cells[3].text = '高'
cells[4].text = '领域适配、风格迁移'
cells = compare_table.rows[3].cells
cells[0].text = '预训练'
cells[1].text = '高'
cells[2].text = '无'
cells[3].text = '中'
cells[4].text = '通用知识'

doc.add_heading('六、总结', level=1)

doc.add_paragraph('RAG 是 LLM 应用的基础技术，通过结合外部知识检索与 LLM 生成，解决知识时效性、私有知识利用和幻觉问题。')

doc.add_paragraph('')
summary_table = doc.add_table(rows=7, cols=2)
summary_table.style = 'Table Grid'
cells = summary_table.rows[0].cells
cells[0].text = '组件'
cells[1].text = '开源推荐'
cells = summary_table.rows[1].cells
cells[0].text = '文档解析'
cells[1].text = 'PyMuPDF, marker-pdf'
cells = summary_table.rows[2].cells
cells[0].text = '文本分割'
cells[1].text = 'LangChain Splitters'
cells = summary_table.rows[3].cells
cells[0].text = '嵌入模型'
cells[1].text = 'BGE, M3E, GTE'
cells = summary_table.rows[4].cells
cells[0].text = '向量数据库'
cells[1].text = 'Chroma, FAISS, Milvus'
cells = summary_table.rows[5].cells
cells[0].text = '检索器'
cells[1].text = '混合检索 + Reranker'
cells = summary_table.rows[6].cells
cells[0].text = 'LLM'
cells[1].text = 'Qwen, DeepSeek, Llama'

doc.add_paragraph('')
doc.add_paragraph('报告生成时间：2026年5月12日')

doc.save('/workspace/RAG_Components_Analysis_Report.docx')
print('RAG 组件分析报告已生成：/workspace/RAG_Components_Analysis_Report.docx')
