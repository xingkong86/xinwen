"""
数据库配置模块 - 使用 SQLAlchemy 2.0 异步写法

需要安装的依赖包：
pip install sqlalchemy aiomysql
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

# 数据库连接 URL
# 格式: mysql+aiomysql://用户名:密码@主机:端口/数据库名 mysql+aiomysql://root:123456@localhost:3306/xinwen
DATABASE_URL = "postgresql+asyncpg://postgres.xfdtlbcutfuvlxfipwda:%40HY18965axy@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # 开发环境下打印 SQL 语句，生产环境建议设为 False
    pool_pre_ping=True,  # 连接池预检查，确保连接有效
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 连接池最大溢出数
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 提交后不过期对象，方便在事务外访问
    autocommit=False,
    autoflush=False,
)


# 声明式基类
class Base(DeclarativeBase):
    """所有模型类的基类"""
    pass


# 异步依赖注入函数，用于 FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的异步生成器
    
    用法示例：
    @app.get("/items/")
    async def read_items(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Item))
        items = result.scalars().all()
        return items
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# 创建所有表的异步函数（可选）
async def create_tables():
    """创建数据库中的所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# 删除所有表的异步函数（可选，谨慎使用）
async def drop_tables():
    """删除数据库中的所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
