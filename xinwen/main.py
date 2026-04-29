"""
FastAPI 主应用入口

新闻爬取与数据可视化系统后端
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from routers import news
from scheduler import start_scheduler, shutdown_scheduler, get_scheduler_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    
    启动时：初始化调度器
    关闭时：关闭调度器
    """
    # 启动时执行
    print("应用启动中...")
    start_scheduler()
    print("调度器已启动，定时爬虫任务已配置")
    
    yield  # 应用运行中
    
    # 关闭时执行
    print("应用关闭中...")
    shutdown_scheduler()
    print("调度器已关闭")


# 创建 FastAPI 应用实例
app = FastAPI(
    title="新闻爬取与数据可视化系统",
    description="提供新闻数据的采集、存储、查询和统计分析功能",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI 文档地址
    redoc_url="/redoc",  # ReDoc 文档地址
    lifespan=lifespan  # 注册生命周期管理
)


# 配置 CORS 跨域中间件（开发阶段允许所有来源）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境建议指定具体域名）
    allow_credentials=True,  # 允许携带凭证（cookies）
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)


# 注册路由模块
app.include_router(news.router)


# 根路由 - 健康检查接口
@app.get(
    "/",
    tags=["系统"],
    summary="健康检查",
    description="检查 API 服务是否正常运行"
)
async def health_check():
    """
    健康检查接口
    
    **用途：**
    - 检查 API 服务是否正常运行
    - 监控系统使用此接口进行健康检测
    - 负载均衡器使用此接口判断服务可用性
    
    **返回：**
    - status: 服务状态
    - message: 欢迎信息
    - timestamp: 当前服务器时间
    - version: API 版本号
    """
    return {
        "status": "healthy",
        "message": "新闻爬取与数据可视化系统 API 正常运行",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# 调度器状态接口
@app.get(
    "/scheduler/status",
    tags=["系统"],
    summary="调度器状态",
    description="查看定时任务调度器的运行状态"
)
async def scheduler_status():
    """
    调度器状态接口
    
    **返回：**
    - running: 调度器是否运行中
    - job_count: 任务数量
    - jobs: 任务列表（包含下次执行时间）
    """
    return get_scheduler_status()
