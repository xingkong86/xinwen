"""
数据模式定义 - 用于 FastAPI 的请求与响应数据校验

使用 Pydantic V2 版本
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class NewsItemBase(BaseModel):
    """新闻条目基础模型"""
    
    title: str = Field(..., max_length=255, description="新闻标题")
    intro: Optional[str] = Field(None, description="新闻简介或原标题")
    keywords: Optional[str] = Field(None, max_length=255, description="分词后的关键词")
    source: Optional[str] = Field(None, max_length=50, description="新闻来源")
    publish_time: Optional[datetime] = Field(None, description="新闻发布时间")


class NewsItemCreate(NewsItemBase):
    """新闻条目创建模型 - 用于数据插入"""
    
    pass


class NewsItemResponse(NewsItemBase):
    """新闻条目响应模型 - 用于接口返回"""
    
    id: int = Field(..., description="新闻ID")
    crawl_time: datetime = Field(..., description="新闻爬取时间")
    
    # Pydantic V2 配置：允许从 ORM 对象转换
    model_config = ConfigDict(from_attributes=True)
