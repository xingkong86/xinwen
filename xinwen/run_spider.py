import asyncio
from database import AsyncSessionLocal
# 引入你 spider.py 里的核心函数
from services.spider import fetch_and_save_news


async def main():
    print("🚀 开始执行定时爬虫任务...")

    # 获取云端数据库会话
    async with AsyncSessionLocal() as db:
        try:
            # 调用你的爬虫函数，默认抓取 sina 来源
            count = await fetch_and_save_news(db, source="sina")
            print(f"✅ 爬虫任务执行完毕，成功抓取并存入 {count} 条新闻！")
        except Exception as e:
            print(f"❌ 爬虫执行失败，错误信息: {e}")


if __name__ == "__main__":
    asyncio.run(main())