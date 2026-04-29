"""
CRUD 操作模块 - 封装针对 NewsItem 模型的数据库操作

使用 SQLAlchemy 2.0 异步写法
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from sqlalchemy.sql import Select
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from collections import Counter

from models import NewsItem
from schemas import NewsItemCreate, NewsItemResponse


async def create_news(db: AsyncSession, news: NewsItemCreate) -> NewsItem:
    """
    创建单条新闻记录
    
    Args:
        db: 异步数据库会话
        news: 新闻创建数据模型
        
    Returns:
        NewsItem: 创建后的新闻对象（包含自动生成的 id 和 crawl_time）
        
    Example:
        news_data = NewsItemCreate(
            title="测试新闻",
            intro="这是一条测试新闻",
            keywords="测试,新闻",
            publish_time=datetime.now()
        )
        new_news = await create_news(db, news_data)
    """
    # 将 Pydantic 模型转换为 ORM 模型
    db_news = NewsItem(**news.model_dump())
    
    # 添加到会话
    db.add(db_news)
    
    # 刷新以获取数据库生成的字段（id, crawl_time）
    await db.flush()
    await db.refresh(db_news)
    
    return db_news


async def get_news_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    keyword: str = None
) -> Tuple[List[NewsItem], int]:
    """
    获取新闻列表，支持分页和关键词筛选
    
    按照 publish_time 倒序排列（最新发布的在前）
    如果 publish_time 为 NULL，则排在最后
    
    Args:
        db: 异步数据库会话
        skip: 跳过的记录数（用于分页）
        limit: 返回的最大记录数（用于分页）
        keyword: 关键词筛选（可选），模糊匹配 keywords 字段
        
    Returns:
        List[NewsItem]: 新闻对象列表
        
    Example:
        # 获取第一页（前10条）
        news_list = await get_news_list(db, skip=0, limit=10)
        
        # 获取包含"人工智能"关键词的新闻
        news_list = await get_news_list(db, skip=0, limit=10, keyword="人工智能")
    """
    # 构建基础查询语句
    base_stmt = select(NewsItem)
    count_stmt = select(func.count(NewsItem.id))
    
    # 添加关键词筛选
    if keyword:
        # 使用 LIKE 进行模糊匹配
        base_stmt = base_stmt.where(NewsItem.keywords.like(f"%{keyword}%"))
        count_stmt = count_stmt.where(NewsItem.keywords.like(f"%{keyword}%"))
        
    # 查询总数
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0
    
    stmt = (
        base_stmt
        .order_by(NewsItem.publish_time.desc(), NewsItem.crawl_time.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # 执行查询
    result = await db.execute(stmt)
    
    # 获取所有结果
    news_list = result.scalars().all()
    
    return list(news_list), total


async def get_news_stats_by_date(
    db: AsyncSession,
    start_date: str = None,
    end_date: str = None
) -> List[Dict[str, Any]]:
    """
    按日期统计新闻数量（用于数据可视化）
    
    根据 publish_time 按天分组统计，返回每天的新闻数量
    注意：publish_time 为 NULL 的记录会被排除
    
    Args:
        db: 异步数据库会话
        start_date: 开始日期，格式：YYYY-MM-DD（可选）
        end_date: 结束日期，格式：YYYY-MM-DD（可选）
        
    Returns:
        List[Dict[str, Any]]: 统计结果列表
        格式: [{"date": "2023-10-01", "count": 10}, {"date": "2023-10-02", "count": 15}, ...]
        
    Example:
        # 查询所有数据
        stats = await get_news_stats_by_date(db)
        
        # 查询指定日期范围
        stats = await get_news_stats_by_date(db, start_date="2023-10-01", end_date="2023-10-31")
    """
    # 构建统计查询
    stmt = (
        select(
            cast(NewsItem.publish_time, Date).label("date"),
            func.count(NewsItem.id).label("count")
        )
        .where(NewsItem.publish_time.is_not(None))
    )
    
    # 添加日期范围过滤
    if start_date:
        stmt = stmt.where(cast(NewsItem.publish_time, Date) >= start_date)
    if end_date:
        stmt = stmt.where(cast(NewsItem.publish_time, Date) <= end_date)
    
    stmt = (
        stmt
        .group_by(cast(NewsItem.publish_time, Date))
        .order_by(cast(NewsItem.publish_time, Date).asc())
    )
    
    # 执行查询
    result = await db.execute(stmt)
    
    # 将结果转换为字典列表
    stats = []
    for row in result:
        stats.append({
            "date": row.date.strftime("%Y-%m-%d") if row.date else None,
            "count": row.count
        })
    
    return stats


async def get_latest_news(db: AsyncSession, limit: int = 10) -> List[NewsItem]:
    """
    获取最新爬取的 N 条新闻
    
    按照 crawl_time 倒序排列（最新爬取的在前）
    
    Args:
        db: 异步数据库会话
        limit: 返回的最大记录数，默认 10 条
        
    Returns:
        List[NewsItem]: 新闻对象列表
        
    Example:
        # 获取最新爬取的 5 条新闻
        latest_news = await get_latest_news(db, limit=5)
    """
    # 构建查询语句
    stmt: Select = (
        select(NewsItem)
        .order_by(NewsItem.crawl_time.desc())  # 按爬取时间倒序
        .limit(limit)
    )
    
    # 执行查询
    result = await db.execute(stmt)
    
    # 获取所有结果
    news_list = result.scalars().all()
    
    return list(news_list)


async def get_keyword_stats(
    db: AsyncSession,
    limit: int = 50,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    获取关键词词频统计（用于词云图）
    
    查询最近 N 天的新闻关键词，在内存中进行词频统计
    
    Args:
        db: 异步数据库会话
        limit: 返回的关键词数量，默认 50 个
        days: 统计最近几天的数据，默认 7 天
        
    Returns:
        List[Dict[str, Any]]: 词云数据列表
        格式: [{"name": "人工智能", "value": 125}, {"name": "经济", "value": 98}, ...]
        
    Example:
        # 获取最近一周的前 50 个热门关键词
        keywords = await get_keyword_stats(db, limit=50, days=7)
        # 返回: [
        #     {"name": "人工智能", "value": 125},
        #     {"name": "经济", "value": 98}
        # ]
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 构建查询：获取最近 N 天的新闻关键词
    stmt = (
        select(NewsItem.keywords)
        .where(NewsItem.keywords.is_not(None))  # 排除空关键词
        .where(NewsItem.keywords != "")  # 排除空字符串
        .where(NewsItem.crawl_time >= start_date)  # 限制时间范围
    )
    
    # 执行查询
    result = await db.execute(stmt)
    keywords_list = result.scalars().all()
    
    # 在内存中进行词频统计
    all_keywords = []
    for keywords_str in keywords_list:
        if keywords_str:
            # 按逗号分割关键词
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            all_keywords.extend(keywords)
    
    # 使用 Counter 统计词频
    counter = Counter(all_keywords)
    
    # 获取前 limit 个高频词
    top_keywords = counter.most_common(limit)
    
    # 转换为词云所需格式
    result_list = [
        {"name": keyword, "value": count}
        for keyword, count in top_keywords
    ]
    
    return result_list


async def get_news_stats_by_source(db: AsyncSession) -> List[Dict[str, Any]]:
    """
    按新闻来源统计数量（用于来源对比分析）
    
    根据 source 字段分组统计，返回各来源的新闻数量
    
    Args:
        db: 异步数据库会话
        
    Returns:
        List[Dict[str, Any]]: 统计结果列表
        格式: [{"source": "sina", "count": 150}, {"source": "netease", "count": 80}, ...]
        
    Example:
        stats = await get_news_stats_by_source(db)
        # 返回: [
        #     {"source": "sina", "count": 150},
        #     {"source": "netease", "count": 80}
        # ]
    """
    # 构建统计查询
    stmt = (
        select(
            NewsItem.source.label("source"),
            func.count(NewsItem.id).label("count")
        )
        .where(NewsItem.source.is_not(None))  # 排除 source 为 NULL 的记录
        .group_by(NewsItem.source)  # 按来源分组
        .order_by(func.count(NewsItem.id).desc())  # 按数量降序排列
    )
    
    # 执行查询
    result = await db.execute(stmt)
    
    # 将结果转换为字典列表
    stats = []
    for row in result:
        stats.append({
            "source": row.source,
            "count": row.count
        })
    
    return stats


async def get_news_stats_by_source_and_date(
    db: AsyncSession,
    days: int = 7
) -> List[Dict[str, Any]]:
    """
    按来源和日期统计新闻数量（用于来源趋势对比）
    
    查询最近 N 天的数据，按来源和日期分组统计
    
    Args:
        db: 异步数据库会话
        days: 统计最近几天的数据，默认 7 天
        
    Returns:
        List[Dict[str, Any]]: 统计结果列表
        格式: [
            {"source": "sina", "date": "2023-10-01", "count": 20},
            {"source": "sina", "date": "2023-10-02", "count": 25},
            {"source": "netease", "date": "2023-10-01", "count": 15}
        ]
        
    Example:
        stats = await get_news_stats_by_source_and_date(db, days=7)
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 构建统计查询
    stmt = (
        select(
            NewsItem.source.label("source"),
            cast(NewsItem.publish_time, Date).label("date"),
            func.count(NewsItem.id).label("count")
        )
        .where(NewsItem.source.is_not(None))
        .where(NewsItem.publish_time.is_not(None))
        .where(NewsItem.publish_time >= start_date)
        .group_by(NewsItem.source, cast(NewsItem.publish_time, Date))
        .order_by(
            cast(NewsItem.publish_time, Date).asc(),
            NewsItem.source.asc()
        )
    )
    
    # 执行查询
    result = await db.execute(stmt)
    
    # 将结果转换为字典列表
    stats = []
    for row in result:
        stats.append({
            "source": row.source,
            "date": row.date.strftime("%Y-%m-%d") if row.date else None,
            "count": row.count
        })
    
    return stats


async def get_overview_stats(db: AsyncSession) -> Dict[str, Any]:
    """
    获取概览统计数据（总数、今日数、关键词数）
    
    Args:
        db: 异步数据库会话
        
    Returns:
        Dict[str, Any]: 统计结果字典
        格式: {
            "total_news": 150,
            "today_news": 10,
            "keyword_count": 50
        }
    """
    from datetime import date
    
    # 1. 查询新闻总数
    total_stmt = select(func.count(NewsItem.id))
    total_result = await db.execute(total_stmt)
    total_news = total_result.scalar() or 0
    
    # 2. 查询今日新增数量（根据 publish_time）
    today = date.today()
    today_stmt = (
        select(func.count(NewsItem.id))
        .where(cast(NewsItem.publish_time, Date) == today)
    )
    today_result = await db.execute(today_stmt)
    today_news = today_result.scalar() or 0
    
    # 3. 查询关键词数量（最近7天的不重复关键词）
    start_date = datetime.now() - timedelta(days=7)
    keywords_stmt = (
        select(NewsItem.keywords)
        .where(NewsItem.keywords.is_not(None))
        .where(NewsItem.keywords != "")
        .where(NewsItem.crawl_time >= start_date)
    )
    keywords_result = await db.execute(keywords_stmt)
    keywords_list = keywords_result.scalars().all()
    
    # 统计不重复关键词数量
    unique_keywords = set()
    for keywords_str in keywords_list:
        if keywords_str:
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            unique_keywords.update(keywords)
    
    keyword_count = len(unique_keywords)
    
    return {
        "total_news": total_news,
        "today_news": today_news,
        "keyword_count": keyword_count
    }


async def get_keyword_timeline(
    db: AsyncSession,
    days: int = 30,
    top_keywords: int = 10
) -> List[Dict[str, Any]]:
    """
    获取关键词时间线数据（用于热点事件时间线可视化）
    
    查询最近 N 天的数据，统计每个关键词每天的出现次数
    
    Args:
        db: 异步数据库会话
        days: 统计最近几天的数据，默认 30 天
        top_keywords: 返回前 N 个热门关键词，默认 10 个
        
    Returns:
        List[Dict[str, Any]]: 时间线数据列表
        格式: [
            {
                "keyword": "人工智能",
                "timeline": [
                    {"date": "2023-10-01", "count": 5},
                    {"date": "2023-10-02", "count": 8},
                    ...
                ],
                "total": 150,
                "peak_date": "2023-10-15",
                "peak_count": 20
            },
            ...
        ]
    """
    # 计算时间范围
    start_date = datetime.now() - timedelta(days=days)
    
    # 1. 先获取热门关键词列表
    keywords_stmt = (
        select(NewsItem.keywords)
        .where(NewsItem.keywords.is_not(None))
        .where(NewsItem.keywords != "")
        .where(NewsItem.crawl_time >= start_date)
    )
    
    keywords_result = await db.execute(keywords_stmt)
    keywords_list = keywords_result.scalars().all()
    
    # 统计关键词频次
    all_keywords = []
    for keywords_str in keywords_list:
        if keywords_str:
            keywords = [k.strip() for k in keywords_str.split(",") if k.strip()]
            all_keywords.extend(keywords)
    
    counter = Counter(all_keywords)
    top_keywords_list = [kw for kw, _ in counter.most_common(top_keywords)]
    
    # 2. 查询每个关键词每天的出现次数
    timeline_data = []
    
    for keyword in top_keywords_list:
        # 查询包含该关键词的新闻，按日期分组统计
        stmt = (
            select(
                cast(NewsItem.publish_time, Date).label("date"),
                func.count(NewsItem.id).label("count")
            )
            .where(NewsItem.keywords.like(f"%{keyword}%"))
            .where(NewsItem.publish_time.is_not(None))
            .where(NewsItem.publish_time >= start_date)
            .group_by(cast(NewsItem.publish_time, Date))
            .order_by(cast(NewsItem.publish_time, Date).asc())
        )
        
        result = await db.execute(stmt)
        daily_counts = result.all()
        
        # 构建时间线数据
        timeline = []
        total_count = 0
        peak_count = 0
        peak_date = None
        
        for row in daily_counts:
            count = row.count
            date_str = row.date.strftime("%Y-%m-%d") if row.date else None
            
            timeline.append({
                "date": date_str,
                "count": count
            })
            
            total_count += count
            
            # 记录峰值
            if count > peak_count:
                peak_count = count
                peak_date = date_str
        
        timeline_data.append({
            "keyword": keyword,
            "timeline": timeline,
            "total": total_count,
            "peak_date": peak_date,
            "peak_count": peak_count
        })
    
    return timeline_data
