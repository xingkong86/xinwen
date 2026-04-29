"""
新闻数据分析 API 路由模块

提供新闻数据的增删改查和统计分析接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from database import get_db
from schemas import NewsItemCreate, NewsItemResponse
import crud
import traceback
from services.spider import fetch_and_save_news

# 创建路由器
router = APIRouter(
    prefix="/api/news",
    tags=["新闻数据分析"]
)


@router.post(
    "/",
    response_model=NewsItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建新闻记录",
    description="接收新闻数据并存入数据库，用于爬虫对接"
)
async def create_news(
    news: NewsItemCreate,
    db: AsyncSession = Depends(get_db)
) -> NewsItemResponse:
    """
    创建单条新闻记录
    
    **用途：** 爬虫程序调用此接口将爬取的新闻数据保存到数据库
    
    **请求体参数：**
    - title: 新闻标题（必填）
    - intro: 新闻简介或原标题（可选）
    - keywords: 分词后的关键词（可选）
    - publish_time: 新闻发布时间（可选）
    
    **返回：**
    - 创建成功的新闻对象，包含自动生成的 id 和 crawl_time
    
    **示例请求：**
    ```json
    {
        "title": "某地发生重大新闻事件",
        "intro": "详细描述...",
        "keywords": "新闻,事件,重大",
        "publish_time": "2023-10-01T12:00:00"
    }
    ```
    """
    try:
        db_news = await crud.create_news(db, news)
        return NewsItemResponse.model_validate(db_news)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建新闻记录失败: {str(e)}"
        )


@router.post(
    "/spider/run",
    summary="手动运行爬虫",
    description="手动触发爬虫程序，爬取新浪新闻数据并保存到数据库"
)
async def run_spider_manually(
    source: str = Query("sina", description="新闻来源，默认sina"),
    db: AsyncSession = Depends(get_db)
):
    """
    手动运行爬虫
    
    **返回：**
    - success: 是否成功
    - count: 爬取并保存的新闻数量
    - message: 提示信息
    """
    try:
        count = await fetch_and_save_news(db, source=source)
        return {
            "success": True,
            "count": count,
            "message": f"爬虫运行成功，新增 {count} 条新闻"
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"爬虫运行失败: {str(e)}"
        )


@router.get(
    "/",
    summary="获取新闻分页列表",
    description="获取新闻列表，支持分页和关键词筛选，按发布时间倒序排列"
)
async def get_news_list(
    skip: int = Query(0, ge=0, description="跳过的记录数（用于分页）"),
    limit: int = Query(50, ge=1, le=100, description="返回的最大记录数（1-100）"),
    keyword: str = Query(None, description="关键词筛选（可选），模糊匹配"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻分页列表
    
    返回包含 items (新闻列表) 和 total (总数) 的字典
    """
    try:
        news_list, total = await crud.get_news_list(db, skip=skip, limit=limit, keyword=keyword)
        items = [NewsItemResponse.model_validate(news) for news in news_list]
        return {
            "items": items,
            "total": total
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取新闻列表失败: {str(e)}"
        )


@router.get(
    "/stats/daily",
    summary="获取每日新闻发布数量统计",
    description="按日期统计新闻发布数量，支持日期范围筛选"
)
async def get_daily_stats(
    start_date: str = Query(None, description="开始日期，格式：YYYY-MM-DD"),
    end_date: str = Query(None, description="结束日期，格式：YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取每日新闻发布数量趋势
    
    **用途：** 前端数据可视化，展示每日新闻发布数量的趋势图
    
    **查询参数：**
    - start_date: 开始日期（可选），格式：YYYY-MM-DD
    - end_date: 结束日期（可选），格式：YYYY-MM-DD
    
    **统计规则：**
    - 根据 publish_time（发布时间）按天分组统计
    - 自动排除 publish_time 为 NULL 的记录
    - 按日期升序排列
    - 如果不指定日期范围，返回所有数据
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": [
            {"date": "2023-10-01", "count": 10},
            {"date": "2023-10-02", "count": 15}
        ],
        "total": 2
    }
    ```
    """
    try:
        stats = await crud.get_news_stats_by_date(db, start_date=start_date, end_date=end_date)
        return {
            "success": True,
            "data": stats,
            "total": len(stats),
            "message": "统计数据获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计数据失败: {str(e)}"
        )


@router.get(
    "/stats/overview",
    summary="获取概览统计数据",
    description="获取新闻总数、今日新增、关键词数等概览数据"
)
async def get_overview_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取概览统计数据
    
    **用途：** 前端顶部统计卡片展示
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": {
            "total_news": 150,
            "today_news": 10,
            "keyword_count": 50
        },
        "message": "概览数据获取成功"
    }
    ```
    
    **说明：**
    - total_news: 数据库中的新闻总数
    - today_news: 今日发布的新闻数量（根据 publish_time）
    - keyword_count: 最近7天的不重复关键词数量
    """
    try:
        stats = await crud.get_overview_stats(db)
        return {
            "success": True,
            "data": stats,
            "message": "概览数据获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取概览数据失败: {str(e)}"
        )


@router.get(
    "/latest",
    response_model=List[NewsItemResponse],
    summary="获取最新爬取的新闻",
    description="获取最近爬取的 10 条新闻，供前端滚动播报展示"
)
async def get_latest_news(
    limit: int = Query(10, ge=1, le=50, description="返回的记录数（1-50），默认 10"),
    db: AsyncSession = Depends(get_db)
) -> List[NewsItemResponse]:
    """
    获取最新爬取的新闻
    
    **用途：** 前端滚动播报、实时新闻展示
    
    **查询参数：**
    - limit: 返回的记录数，默认 10，最大 50
    
    **排序规则：**
    - 按 crawl_time（爬取时间）倒序排列
    - 返回最新爬取的新闻
    
    **返回：**
    - 新闻对象列表
    
    **使用场景：**
    - 首页滚动播报
    - 实时新闻更新提醒
    - 最新动态展示
    """
    try:
        news_list = await crud.get_latest_news(db, limit=limit)
        return [NewsItemResponse.model_validate(news) for news in news_list]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取最新新闻失败: {str(e)}"
        )


@router.get(
    "/stats/keywords",
    summary="获取关键词词频统计",
    description="统计最近一周新闻关键词词频，供前端词云图展示"
)
async def get_keyword_stats(
    limit: int = Query(50, ge=1, le=200, description="返回的关键词数量（1-200），默认 50"),
    days: int = Query(7, ge=1, le=30, description="统计最近几天的数据（1-30），默认 7 天"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取关键词词频统计（词云数据）
    
    **用途：** 前端词云图展示热门关键词
    
    **查询参数：**
    - limit: 返回的关键词数量，默认 50，最大 200
    - days: 统计最近几天的数据，默认 7 天，最大 30 天
    
    **统计规则：**
    - 查询最近 N 天的新闻 keywords 字段
    - 按逗号分割关键词
    - 使用 Counter 统计词频
    - 按频次降序排列
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": [
            {"name": "人工智能", "value": 125},
            {"name": "经济", "value": 98},
            {"name": "科技", "value": 76}
        ],
        "total": 50,
        "message": "关键词统计获取成功"
    }
    ```
    
    **可视化建议：**
    - 词云图：关键词大小与频次成正比
    - 柱状图：展示 Top 10 热门关键词
    """
    try:
        stats = await crud.get_keyword_stats(db, limit=limit, days=days)
        return {
            "success": True,
            "data": stats,
            "total": len(stats),
            "message": "关键词统计获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取关键词统计失败: {str(e)}"
        )


@router.get(
    "/stats/source",
    summary="获取新闻来源统计",
    description="统计各新闻来源的数量，供前端饼图/柱状图展示"
)
async def get_source_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻来源统计
    
    **用途：** 前端数据可视化，展示各新闻来源的占比和数量
    
    **统计规则：**
    - 根据 source（新闻来源）字段分组统计
    - 自动排除 source 为 NULL 的记录
    - 按数量降序排列
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": [
            {"source": "sina", "count": 150},
            {"source": "netease", "count": 80},
            {"source": "toutiao", "count": 45}
        ],
        "total": 3,
        "message": "来源统计获取成功"
    }
    ```
    
    **可视化建议：**
    - 饼图：展示各来源的占比
    - 柱状图：对比不同来源的新闻数量
    - 环形图：美观展示来源分布
    """
    try:
        stats = await crud.get_news_stats_by_source(db)
        return {
            "success": True,
            "data": stats,
            "total": len(stats),
            "message": "来源统计获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取来源统计失败: {str(e)}"
        )


@router.get(
    "/stats/source-trend",
    summary="获取新闻来源趋势统计",
    description="统计最近N天各来源的新闻发布趋势，供前端多系列折线图展示"
)
async def get_source_trend_stats(
    days: int = Query(7, ge=1, le=30, description="统计最近几天的数据（1-30），默认 7 天"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取新闻来源趋势统计
    
    **用途：** 前端数据可视化，展示各新闻来源的发布趋势对比
    
    **查询参数：**
    - days: 统计最近几天的数据，默认 7 天，最大 30 天
    
    **统计规则：**
    - 查询最近 N 天的新闻数据
    - 按来源和日期分组统计
    - 按日期升序排列
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": [
            {"source": "sina", "date": "2023-10-01", "count": 20},
            {"source": "sina", "date": "2023-10-02", "count": 25},
            {"source": "netease", "date": "2023-10-01", "count": 15},
            {"source": "netease", "date": "2023-10-02", "count": 18}
        ],
        "total": 4,
        "message": "来源趋势统计获取成功"
    }
    ```
    
    **可视化建议：**
    - 多系列折线图：每个来源一条线，对比趋势
    - 堆叠面积图：展示各来源的累积趋势
    - 分组柱状图：对比不同日期各来源的数量
    """
    try:
        stats = await crud.get_news_stats_by_source_and_date(db, days=days)
        return {
            "success": True,
            "data": stats,
            "total": len(stats),
            "message": "来源趋势统计获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取来源趋势统计失败: {str(e)}"
        )


@router.get(
    "/stats/keyword-timeline",
    summary="获取关键词时间线数据",
    description="统计热门关键词在时间轴上的出现趋势，用于热点事件时间线可视化"
)
async def get_keyword_timeline(
    days: int = Query(30, ge=7, le=90, description="统计最近几天的数据（7-90），默认 30 天"),
    top_keywords: int = Query(10, ge=5, le=20, description="返回前 N 个热门关键词（5-20），默认 10 个"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取关键词时间线数据
    
    **用途：** 前端热点事件时间线可视化，展示关键词的爆发与消退过程
    
    **查询参数：**
    - days: 统计最近几天的数据，默认 30 天，范围 7-90 天
    - top_keywords: 返回前 N 个热门关键词，默认 10 个，范围 5-20 个
    
    **返回格式：**
    ```json
    {
        "success": true,
        "data": [
            {
                "keyword": "人工智能",
                "timeline": [
                    {"date": "2023-10-01", "count": 5},
                    {"date": "2023-10-02", "count": 8}
                ],
                "total": 150,
                "peak_date": "2023-10-15",
                "peak_count": 20
            }
        ],
        "total": 10,
        "message": "关键词时间线数据获取成功"
    }
    ```
    
    **可视化建议：**
    - 时间线图：展示关键词的生命周期
    - 河流图：展示多个关键词的趋势对比
    - 热力图：展示关键词在不同时间的热度
    """
    try:
        timeline_data = await crud.get_keyword_timeline(db, days=days, top_keywords=top_keywords)
        return {
            "success": True,
            "data": timeline_data,
            "total": len(timeline_data),
            "message": "关键词时间线数据获取成功"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取关键词时间线数据失败: {str(e)}"
        )
