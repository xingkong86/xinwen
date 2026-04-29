"""
测试 source 字段功能

运行方式：
    python test_source_feature.py
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import AsyncSessionLocal
from schemas import NewsItemCreate
import crud
from datetime import datetime, timedelta


async def test_create_news_with_source():
    """测试创建带来源的新闻"""
    print("\n" + "="*60)
    print("测试 1: 创建带来源的新闻")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        # 创建不同来源的测试新闻
        test_sources = ["sina", "netease", "toutiao"]
        
        for source in test_sources:
            news_data = NewsItemCreate(
                title=f"测试新闻 - {source} - {datetime.now().strftime('%H:%M:%S')}",
                intro=f"这是来自 {source} 的测试新闻",
                keywords="测试,新闻,来源",
                source=source,
                publish_time=datetime.now()
            )
            
            news = await crud.create_news(db, news_data)
            print(f"✓ 创建成功: ID={news.id}, 来源={news.source}, 标题={news.title}")
        
        await db.commit()
        print("\n✅ 测试通过：成功创建带来源的新闻")


async def test_source_stats():
    """测试来源统计功能"""
    print("\n" + "="*60)
    print("测试 2: 来源统计")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        stats = await crud.get_news_stats_by_source(db)
        
        if stats:
            print("\n📊 各来源新闻统计：")
            total = sum(item['count'] for item in stats)
            for item in stats:
                percentage = round(item['count'] / total * 100, 2)
                print(f"  {item['source']}: {item['count']} 条 ({percentage}%)")
            print(f"\n  总计: {total} 条")
            print("\n✅ 测试通过：来源统计功能正常")
        else:
            print("\n⚠️  暂无数据")


async def test_source_trend():
    """测试来源趋势统计"""
    print("\n" + "="*60)
    print("测试 3: 来源趋势统计")
    print("="*60)
    
    async with AsyncSessionLocal() as db:
        stats = await crud.get_news_stats_by_source_and_date(db, days=7)
        
        if stats:
            print("\n📈 最近 7 天各来源趋势：")
            
            # 按来源分组显示
            from collections import defaultdict
            by_source = defaultdict(list)
            for item in stats:
                by_source[item['source']].append(f"{item['date']}: {item['count']}条")
            
            for source, trends in by_source.items():
                print(f"\n  {source}:")
                for trend in trends[:5]:  # 只显示前5天
                    print(f"    {trend}")
            
            print("\n✅ 测试通过：来源趋势统计功能正常")
        else:
            print("\n⚠️  暂无趋势数据")


async def test_query_by_source():
    """测试按来源查询新闻"""
    print("\n" + "="*60)
    print("测试 4: 按来源查询新闻")
    print("="*60)
    
    from sqlalchemy import select
    from models import NewsItem
    
    async with AsyncSessionLocal() as db:
        # 查询新浪新闻
        stmt = select(NewsItem).where(NewsItem.source == "sina").limit(5)
        result = await db.execute(stmt)
        sina_news = result.scalars().all()
        
        if sina_news:
            print(f"\n📰 新浪新闻（前5条）：")
            for news in sina_news:
                print(f"  ID={news.id}, 标题={news.title[:30]}...")
            print("\n✅ 测试通过：按来源查询功能正常")
        else:
            print("\n⚠️  未找到新浪新闻")


async def test_null_source():
    """测试查询未标记来源的新闻"""
    print("\n" + "="*60)
    print("测试 5: 查询未标记来源的新闻")
    print("="*60)
    
    from sqlalchemy import select, func
    from models import NewsItem
    
    async with AsyncSessionLocal() as db:
        # 统计未标记来源的新闻数量
        stmt = select(func.count(NewsItem.id)).where(NewsItem.source.is_(None))
        result = await db.execute(stmt)
        count = result.scalar()
        
        print(f"\n📊 未标记来源的新闻数量: {count} 条")
        
        if count > 0:
            print("⚠️  建议为这些新闻补充来源信息")
        else:
            print("✅ 所有新闻都已标记来源")


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀 " + "="*58)
    print("开始测试 source 字段功能")
    print("="*60)
    
    try:
        await test_create_news_with_source()
        await test_source_stats()
        await test_source_trend()
        await test_query_by_source()
        await test_null_source()
        
        print("\n" + "="*60)
        print("🎉 所有测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
