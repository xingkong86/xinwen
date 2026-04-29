"""
数据模型定义 - 新闻数据 ORM 模型
"""

from sqlalchemy import String, Text, DateTime, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from database import Base


class NewsItem(Base):
    """新闻条目模型"""
    
    __tablename__ = "news_item"
    
    # 主键ID，自增
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
        comment="新闻ID，主键"
    )
    
    # 新闻标题，不能为空，加索引
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="新闻标题"
    )
    
    # 新闻简介或原标题，允许为空
    intro: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="新闻简介或原标题"
    )
    
    # 关键词，允许为空
    keywords: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="分词后的关键词"
    )
    
    # 新闻来源，允许为空，加索引便于来源分析
    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="新闻来源（如：sina, netease, toutiao 等）"
    )
    
    # 发布时间，允许为空
    publish_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="新闻发布时间"
    )
    
    # 爬取时间，默认为当前时间
    crawl_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="新闻爬取时间"
    )
    
    def __repr__(self) -> str:
        """模型的字符串表示"""
        return f"<NewsItem(id={self.id}, title='{self.title}', publish_time={self.publish_time})>"
