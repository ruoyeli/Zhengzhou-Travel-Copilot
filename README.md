基于 LangGraph + RAG + FastAPI 构建的郑州本地 AI 旅游助手，支持实时天气查询与景点智能导览。

项目效果：

实时天气查询 — 调用 Open-Meteo 免费接口，返回真实天气数据，拒绝幻觉

RAG 景点导览 — 基于本地 PDF 文档构建向量知识库，回答严格来自资料，可验证

流式输出 — 采用 SSE 流式传输，字符逐步显示，告别等待

防幻觉验证 — 界面实时展示工具调用过程和原始返回数据，用户可自行核查

向量库持久化 — FAISS 索引保存本地，二次启动秒级加载

前后端分离 — FastAPI 后端 + Streamlit 前端，结构清晰专业



技术栈：

模块技术AI框架-----------LangChain + LangGraph

大模型-------------------DeepSeek

向量数据库---------------FAISS

Embedding---------------sentence-transformers

后端---------------------FastAPI + uvicorn

前端---------------------Streamlit

异步---------------------HTTPhttpx



Zhengzhou-Travel-Copilot/
├── frontend/app.py          # Streamlit 前端界面

├── backend/

│   ├── main.py              # FastAPI 入口

│   ├── api/routes.py        # API 路由

│   ├── services/            # Agent 业务逻辑

│   ├── tools/               # 天气工具 + RAG检索工具

│   ├── schemas/             # 数据模型

│   └── core/config.py       # 配置管理

├── resources/erzhi.pdf      # 景点知识库

├── run.py                   # 一键启动后端

└── requirements.txt
