import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import uvicorn
from backend.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001, reload=False)