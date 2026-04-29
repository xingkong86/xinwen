"""
数据库迁移脚本：为 news_item 表添加 source 字段

运行方式：
    python migrations/add_source_field.py

功能：
    1. 添加 source 字段（VARCHAR(50)，可为空，带索引）
    2. 为现有数据设置默认来源为 'sina'
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from database import engine, AsyncSessionLocal


async def add_source_field():
    """添加 source 字段到 news_item 表"""
    
    async with engine.begin() as conn:
        print("开始数据库迁移：添加 source 字段...")
        
        try:
            # 1. 检查字段是否已存在
            check_sql = text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'news_item' 
                AND column_name = 'source'
            """)
            
            result = await conn.execute(check_sql)
            exists = result.scalar()
            
            if exists > 0:
                print("✓ source 字段已存在，跳过迁移")
                return
            
            # 2. 添加 source 字段
            add_column_sql = text("""
                ALTER TABLE news_item 
                ADD COLUMN source VARCHAR(50) NULL 
                COMMENT '新闻来源（如：sina, netease, toutiao 等）'
            """)
            
            await conn.execute(add_column_sql)
            print("✓ 成功添加 source 字段")
            
            # 3. 为现有数据设置默认值
            update_sql = text("""
                UPDATE news_item 
                SET source = 'sina' 
                WHERE source IS NULL
            """)
            
            result = await conn.execute(update_sql)
            print(f"✓ 已为 {result.rowcount} 条现有数据设置默认来源为 'sina'")
            
            # 4. 创建索引
            create_index_sql = text("""
                CREATE INDEX ix_news_item_source 
                ON news_item (source)
            """)
            
            await conn.execute(create_index_sql)
            print("✓ 成功创建 source 字段索引")
            
            print("\n✅ 数据库迁移完成！")
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {e}")
            raise


async def verify_migration():
    """验证迁移结果"""
    
    async with AsyncSessionLocal() as db:
        # 查询表结构
        result = await db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_comment
            FROM information_schema.columns
            WHERE table_name = 'news_item'
            AND column_name = 'source'
        """))
        
        row = result.fetchone()
        
        if row:
            print("\n📊 字段信息：")
            print(f"  字段名: {row[0]}")
            print(f"  数据类型: {row[1]}")
            print(f"  可为空: {row[2]}")
            print(f"  注释: {row[3]}")
            
            # 统计各来源的新闻数量
            stats_result = await db.execute(text("""
                SELECT source, COUNT(*) as count
                FROM news_item
                GROUP BY source
                ORDER BY count DESC
            """))
            
            print("\n📈 各来源新闻统计：")
            for source, count in stats_result:
                print(f"  {source or '(未知)'}: {count} 条")
        else:
            print("\n⚠️  未找到 source 字段")


async def main():
    """主函数"""
    try:
        # 执行迁移
        await add_source_field()
        
        # 验证迁移
        await verify_migration()
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
