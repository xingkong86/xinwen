# api/index.py
from fastapi import FastAPI
from routers import news # 引入你之前写的路由

app = FastAPI(title="News API")
app.include_router(news.router)

# Vercel 需要暴露 app 实例