import os
from langchain_core.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from backend.core.config import PDF_PATH, FAISS_INDEX_PATH

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

def get_vectorstore() -> FAISS:
    # 如果本地已有索引，直接加载（秒级启动）
    if os.path.exists(FAISS_INDEX_PATH):
        print("✅ 从本地加载FAISS索引...")
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    # 第一次运行，从PDF创建并保存
    print("⏳ 首次运行，从PDF创建FAISS索引（只需一次）...")
    loader = PyPDFLoader(PDF_PATH)
    pages = loader.load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    ).split_documents(pages)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(FAISS_INDEX_PATH)
    print(f"✅ 索引已保存到 {FAISS_INDEX_PATH}，下次启动将秒级加载")
    return vs

# 模块加载时初始化一次
vectorstore = get_vectorstore()

@tool
def search_erzhi_tower(query: str) -> str:
    """
    当用户询问郑州二七纪念塔、二七广场、二七罢工历史、
    建筑、门票、交通等相关问题时必须调用。
    只回答资料中有的内容，不能编造。
    """
    docs = vectorstore.similarity_search(query, k=3)
    result = "\n\n".join([doc.page_content for doc in docs])
    return f"【来自景点PDF资料，非AI编造】：\n{result}"