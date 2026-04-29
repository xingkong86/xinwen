"""
检查数据库中的新闻数据
"""

import asyncio
from database import AsyncSessionLocal
from crud import get_news_list, get_keyword_stats


async def check_data():
    """检查数据库中的数据"""
    async with AsyncSessionLocal() as db:
        # 获取新闻列表
        news_list = await get_news_list(db, skip=0, limit=10)
        
        print(f"\n=== 数据库中共有 {len(news_list)} 条新闻（显示前10条）===\n")
        
        for i, news in enumerate(news_list, 1):
            print(f"{i}. {news.title}")
            print(f"   关键词: {news.keywords}")
            print(f"   发布时间: {news.publish_time}")
            print(f"   爬取时间: {news.crawl_time}")
            print()
        
        # 获取关键词统计
        keywords = await get_keyword_stats(db, limit=10, days=7)
        
        print("\n=== 热门关键词 Top 10 ===\n")
        for i, kw in enumerate(keywords, 1):
            print(f"{i}. {kw['name']}: {kw['value']} 次")


if __name__ == "__main__":
    asyncio.run(check_data())
