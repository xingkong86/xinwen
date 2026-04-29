"""
数据库初始化脚本

用于在开发初期创建数据库表结构
运行方式: python init_db.py
"""

import asyncio
from database import engine, Base
# 导入所有模型，确保它们被注册到 Base.metadata
from models import NewsItem


async def init_models():
    """
    初始化数据库表结构
    
    使用异步方式创建所有在 Base.metadata 中注册的表
    """
    print("开始初始化数据库...")
    
    try:
        async with engine.begin() as conn:
            # 使用 run_sync 在异步上下文中执行同步的 create_all 方法
            await conn.run_sync(Base.metadata.create_all)
        
        print("数据库表创建成功！")
        print(f"已创建的表: {', '.join(Base.metadata.tables.keys())}")
    finally:
        # 确保引擎正确关闭，释放所有连接
        await engine.dispose()


async def drop_models():
    """
    删除所有数据库表（谨慎使用）
    
    用于开发环境重置数据库
    """
    print("警告：即将删除所有数据库表...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        
        print("所有表已删除！")
    finally:
        # 确保引擎正确关闭，释放所有连接
        await engine.dispose()


if __name__ == "__main__":
    # 执行数据库初始化
    asyncio.run(init_models())
    
    # 如果需要重置数据库，可以先删除再创建
    # asyncio.run(drop_models())
    # asyncio.run(init_models())
