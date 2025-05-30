#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新社区帖子表字段
将community_posts表中的likes字段改为likes_count
"""

import sys
import os
import sqlite3

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from config import config

def update_community_likes_field():
    """更新社区帖子表字段名"""
    print("开始修改community_posts表结构...")
    
    # 获取数据库文件路径
    app = create_app('development')
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    
    if db_uri.startswith('sqlite:///'):
        # SQLite数据库
        db_path = db_uri.replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"数据库文件 {db_path} 不存在")
            return False
        
        try:
            # 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(community_posts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 检查是否已经有likes_count字段
            if 'likes_count' in columns:
                print("表已经有likes_count字段，无需修改")
                
                # 如果同时存在likes和likes_count，需要处理迁移数据
                if 'likes' in columns:
                    print("同时存在likes和likes_count字段，将likes的数据复制到likes_count")
                    cursor.execute("UPDATE community_posts SET likes_count = likes WHERE likes_count IS NULL")
                    conn.commit()
                
                conn.close()
                return True
            
            # 检查是否有likes字段
            if 'likes' not in columns:
                print("表中没有likes字段，直接添加likes_count字段")
                cursor.execute("ALTER TABLE community_posts ADD COLUMN likes_count INTEGER DEFAULT 0")
                conn.commit()
                conn.close()
                return True
            
            # SQLite不支持直接重命名列，需要创建新表
            print("重命名字段: likes -> likes_count")
            
            # 获取表的完整结构
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='community_posts'")
            create_sql = cursor.fetchone()[0]
            
            # 替换字段名
            new_create_sql = create_sql.replace('likes INTEGER', 'likes_count INTEGER')
            
            # 创建新表结构的临时表
            cursor.execute("DROP TABLE IF EXISTS community_posts_new")
            cursor.execute(new_create_sql.replace('CREATE TABLE community_posts', 'CREATE TABLE community_posts_new'))
            
            # 构造INSERT语句，将原表数据复制到新表
            cursor.execute("PRAGMA table_info(community_posts)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 替换likes为likes_count
            new_columns = [col if col != 'likes' else 'likes_count' for col in columns]
            
            # 构造INSERT语句
            insert_sql = f"INSERT INTO community_posts_new ({', '.join(new_columns)}) SELECT {', '.join(columns)} FROM community_posts"
            cursor.execute(insert_sql)
            
            # 删除原表并重命名新表
            cursor.execute("DROP TABLE community_posts")
            cursor.execute("ALTER TABLE community_posts_new RENAME TO community_posts")
            
            # 提交事务
            conn.commit()
            
            print("表结构修改完成，已将likes字段更改为likes_count")
            conn.close()
            return True
            
        except Exception as e:
            print(f"修改表结构时出错: {str(e)}")
            return False
    else:
        print(f"不支持的数据库类型: {db_uri}")
        return False

if __name__ == '__main__':
    update_community_likes_field() 