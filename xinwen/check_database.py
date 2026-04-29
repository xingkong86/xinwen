"""
检查数据库中的新闻数据
"""
import asyncio
from sqlalchemy import select, func
from database import AsyncSessionLocal
from models import NewsItem

async def check_data():
    async with AsyncSessionLocal() as db:
        # 查询新闻总数
        total_stmt = select(func.count(NewsItem.id))
        total_result = await db.execute(total_stmt)
        total = total_result.scalar()
        
        print(f"数据库中新闻总数: {total}")
        
        if total > 0:
            # 查询最新的5条新闻
            latest_stmt = select(NewsItem).order_by(NewsItem.crawl_time.desc()).limit(5)
            latest_result = await db.execute(latest_stmt)
            latest_news = latest_result.scalars().all()
            
            print("\n最新的5条新闻:")
            for news in latest_news:
                print(f"  ID: {news.id}, 标题: {news.title[:30]}...")
        else:
            print("\n数据库中没有新闻数据！")
            print("请运行爬虫获取数据:")
            print("  cd xinwen")
            print("  python services/spider.py")

if __name__ == "__main__":
    asyncio.run(check_data())
