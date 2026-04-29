"""
新闻爬虫服务模块 - 异步爬取新闻数据并存入数据库

依赖安装：
pip install httpx jieba
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import httpx
import jieba
import jieba.analyse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import NewsItem
from schemas import NewsItemCreate
from crud import create_news

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_keywords(text: str, top_n: int = 5) -> str:
    """
    从文本中提取关键词
    
    使用 TextRank 算法提取关键词，返回前 top_n 个关键词
    
    Args:
        text: 待提取关键词的文本
        top_n: 返回的关键词数量，默认 5 个
        
    Returns:
        str: 用逗号拼接的关键词字符串
        
    Example:
        keywords = extract_keywords("这是一段关于人工智能的新闻报道")
        # 返回: "人工智能,新闻,报道"
    """
    if not text or not text.strip():
        return ""
    
    try:
        # 使用 TextRank 提取关键词
        keywords = jieba.analyse.textrank(
            text,
            topK=top_n,
            withWeight=False,
            allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a')  # 名词、动词、形容词等
        )
        
        # 如果 TextRank 结果不足，尝试使用 TF-IDF
        if len(keywords) < top_n:
            tfidf_keywords = jieba.analyse.extract_tags(
                text,
                topK=top_n,
                withWeight=False,
                allowPOS=('n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'a')
            )
            # 合并去重
            all_keywords = list(keywords) + [k for k in tfidf_keywords if k not in keywords]
            keywords = all_keywords[:top_n]
        
        return ",".join(keywords)
    
    except Exception as e:
        logger.error(f"提取关键词失败: {e}")
        return ""


async def check_news_exists(db: AsyncSession, title: str) -> bool:
    """
    检查新闻是否已存在（按标题去重）
    
    Args:
        db: 异步数据库会话
        title: 新闻标题
        
    Returns:
        bool: True 表示已存在，False 表示不存在
    """
    stmt = select(NewsItem).where(NewsItem.title == title)
    result = await db.execute(stmt)
    return result.scalar_one_or_none() is not None


def parse_timestamp(intime: str) -> Optional[datetime]:
    """
    解析新浪新闻的时间戳字符串
    
    Args:
        intime: 时间戳字符串，如 "1704067200" 或 "1704067200000"
        
    Returns:
        datetime: 解析后的时间对象，解析失败返回 None
    """
    if not intime:
        return None
    
    try:
        # 判断是秒级还是毫秒级时间戳
        ts = int(intime)
        if ts > 10000000000:  # 毫秒级
            ts = ts / 1000
        return datetime.fromtimestamp(ts)
    except (ValueError, OSError) as e:
        logger.debug(f"无法解析时间戳: {intime}, 错误: {e}")
        return None


async def fetch_sina_news(db: AsyncSession, page: int = 1, num: int = 50) -> int:
    """
    爬取新浪新闻 JSON 接口
    
    Args:
        db: 异步数据库会话
        page: 页码，默认 1
        num: 每页数量，默认 50
        
    Returns:
        int: 成功保存的新闻数量
    """
    saved_count = 0
    
    # 新浪滚动新闻 JSON 接口
    url = "https://feed.mix.sina.com.cn/api/roll/get"
    
    params = {
        "pageid": 153,
        "lid": 2509,
        "k": "",
        "num": num,
        "page": page
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'https://news.sina.com.cn/',
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            # 解析 JSON 数据
            data = response.json()
            
            # 检查返回状态（code=0 表示成功）
            result = data.get("result", {})
            status = result.get("status", {})
            
            if status.get("code") != 0:
                logger.error(f"接口返回错误: {data}")
                return 0
            
            # 获取新闻列表
            news_list = result.get("data", [])
            
            if not news_list:
                logger.warning("未获取到新闻数据")
                return 0
            
            logger.info(f"获取到 {len(news_list)} 条新闻条目")
            
            for item in news_list:
                try:
                    # 提取标题
                    title = item.get("title")
                    if not title:
                        continue
                    
                    # 检查是否已存在
                    if await check_news_exists(db, title):
                        logger.debug(f"新闻已存在，跳过: {title}")
                        continue
                    
                    # 提取简介
                    intro = item.get("intro") or item.get("summary") or item.get("digest")
                    
                    # 提取发布时间（intime 是时间戳字符串）
                    intime = item.get("intime")
                    publish_time = parse_timestamp(intime)
                    
                    # 提取关键词
                    keyword_text = f"{title} {intro or ''}"
                    keywords = extract_keywords(keyword_text)
                    
                    # 创建新闻数据
                    news_data = NewsItemCreate(
                        title=title,
                        intro=intro,
                        keywords=keywords,
                        source="sina",  # 标记新闻来源
                        publish_time=publish_time
                    )
                    
                    # 保存到数据库
                    await create_news(db, news_data)
                    saved_count += 1
                    logger.info(f"成功保存新闻: {title}")
                    
                except Exception as e:
                    logger.error(f"处理新闻条目失败: {e}")
                    continue
            
            # 提交事务
            await db.commit()
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP 请求失败: {e}")
    except httpx.RequestError as e:
        logger.error(f"网络请求错误: {e}")
    except Exception as e:
        logger.error(f"爬取新闻失败: {e}")
        await db.rollback()
    
    return saved_count


async def fetch_netease_news(db: AsyncSession) -> int:
    """
    爬取网易新闻（已弃用，保留接口兼容）
    
    Args:
        db: 异步数据库会话
        
    Returns:
        int: 成功保存的新闻数量
    """
    logger.warning("网易新闻爬虫已弃用，建议使用新浪新闻源")
    return 0


async def fetch_and_save_news(db: AsyncSession, source: str = "sina") -> int:
    """
    核心异步函数：爬取新闻并保存到数据库
    
    Args:
        db: 异步数据库会话
        source: 新闻来源，可选 "sina" 或 "netease"，默认 "sina"
        
    Returns:
        int: 成功保存的新闻数量
        
    Example:
        async with AsyncSessionLocal() as db:
            count = await fetch_and_save_news(db, source="sina")
            print(f"成功保存 {count} 条新闻")
    """
    logger.info(f"开始爬取新闻，来源: {source}")
    
    if source == "sina":
        count = await fetch_sina_news(db)
    elif source == "netease":
        count = await fetch_netease_news(db)
    else:
        logger.warning(f"未知的新闻来源: {source}，使用默认来源 sina")
        count = await fetch_sina_news(db)
    
    logger.info(f"爬取完成，成功保存 {count} 条新闻")
    return count


# 测试代码
if __name__ == "__main__":
    import asyncio
    from database import AsyncSessionLocal
    
    async def test():
        """测试爬虫功能"""
        async with AsyncSessionLocal() as db:
            # 测试关键词提取
            test_text = "人工智能技术正在快速发展，深度学习和机器学习成为热门话题"
            keywords = extract_keywords(test_text)
            print(f"关键词: {keywords}")
            
            # 测试爬虫
            count = await fetch_and_save_news(db, source="sina")
            print(f"保存了 {count} 条新闻")
    
    # 运行测试
    asyncio.run(test())
