import os
from dotenv import load_dotenv

# 从项目根目录加载.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

# 资源路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
PDF_PATH = os.path.join(BASE_DIR, "resources", "erzhi.pdf")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_index")  # 持久化索引存这里