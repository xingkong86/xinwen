"""
定时任务调度器模块 - 使用 APScheduler 管理后台定时任务

依赖安装：
pip install apscheduler
"""

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database import AsyncSessionLocal
from services.spider import fetch_and_save_news

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建调度器实例
scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def scheduled_news_crawl():
    """
    定时爬取新闻任务
    
    为定时任务创建独立的数据库会话，执行爬虫后自动关闭
    """
    logger.info("开始执行定时爬虫任务...")
    
    try:
        # 为定时任务创建独立的数据库会话
        async with AsyncSessionLocal() as db:
            try:
                # 爬取新浪新闻
                sina_count = await fetch_and_save_news(db, source="sina")
                logger.info(f"新浪新闻爬取完成，保存 {sina_count} 条")
                
                # 爬取网易新闻
                netease_count = await fetch_and_save_news(db, source="netease")
                logger.info(f"网易新闻爬取完成，保存 {netease_count} 条")
                
                # 提交事务
                await db.commit()
                
                total = sina_count + netease_count
                logger.info(f"定时爬虫任务完成，共保存 {total} 条新闻")
                
            except Exception as e:
                await db.rollback()
                logger.error(f"定时爬虫任务执行失败: {e}")
                raise
                
    except Exception as e:
        logger.error(f"数据库会话创建失败: {e}")


def setup_scheduler():
    """
    配置调度器，添加定时任务
    
    任务配置：
    - 每隔 8 小时执行一次新闻爬取
    - 任务 ID: news_crawl_job
    """
    # 添加定时任务：每隔 8 小时执行一次
    scheduler.add_job(
        scheduled_news_crawl,
        trigger=IntervalTrigger(hours=8),
        id="news_crawl_job",
        name="新闻爬取定时任务",
        replace_existing=True,  # 如果已存在则替换
        max_instances=1,  # 同一时间只允许一个实例运行
        misfire_grace_time=3600,  # 允许 1 小时的错过容忍时间
    )
    
    logger.info("调度器配置完成，已添加新闻爬取定时任务（每 8 小时执行一次）")


def start_scheduler():
    """
    启动调度器
    """
    if not scheduler.running:
        setup_scheduler()
        scheduler.start()
        logger.info("调度器已启动")
    else:
        logger.warning("调度器已在运行中")


def shutdown_scheduler():
    """
    关闭调度器
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)  # 等待正在执行的任务完成
        logger.info("调度器已关闭")
    else:
        logger.warning("调度器未在运行")


def get_scheduler_status() -> dict:
    """
    获取调度器状态信息
    
    Returns:
        dict: 包含调度器状态和任务信息的字典
    """
    jobs = scheduler.get_jobs()
    
    return {
        "running": scheduler.running,
        "job_count": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            }
            for job in jobs
        ]
    }


# 手动触发爬虫的函数（用于测试或手动执行）
async def trigger_crawl_manually(source: str = "sina") -> int:
    """
    手动触发爬虫任务
    
    Args:
        source: 新闻来源，"sina" 或 "netease"
        
    Returns:
        int: 保存的新闻数量
    """
    logger.info(f"手动触发爬虫任务，来源: {source}")
    
    async with AsyncSessionLocal() as db:
        try:
            count = await fetch_and_save_news(db, source=source)
            await db.commit()
            return count
        except Exception as e:
            await db.rollback()
            logger.error(f"手动爬虫任务失败: {e}")
            raise
