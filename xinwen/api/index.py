# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import news # 引入你之前写的路由

app = FastAPI(title="News API")

# 必须在这里加上 CORS 配置，Vercel 才能允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端域名访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法 (GET, POST等)
    allow_headers=["*"],  # 允许所有请求头
)

app.include_router(news.router)

# Vercel 需要暴露 app 实例