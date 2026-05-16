from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="郑州AI旅游助手", version="1.0.0")
app.include_router(router)

@app.get("/")
def root():
    return {"status": "运行中", "服务": "郑州AI旅游助手"}