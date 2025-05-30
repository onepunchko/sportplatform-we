#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修复社区帖子点赞数与实际点赞记录的同步问题
确保每个帖子的likes_count值与post_likes表中的实际记录数一致
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import CommunityPost, PostLike

def fix_community_likes():
    """修复社区帖子点赞数据同步问题"""
    print("开始修复社区帖子点赞数据...")
    
    # 创建Flask应用上下文
    app = create_app('development')
    with app.app_context():
        try:
            # 获取所有帖子
            posts = CommunityPost.query.all()
            print(f"共获取到 {len(posts)} 条帖子")
            
            # 遍历每条帖子，修正点赞数
            updated_count = 0
            for post in posts:
                # 计算实际点赞数
                actual_likes_count = PostLike.query.filter_by(post_id=post.id).count()
                
                # 如果不一致，更新帖子的点赞数
                if post.likes_count != actual_likes_count:
                    print(f"修正帖子ID={post.id}: 点赞数 {post.likes_count} -> {actual_likes_count}")
                    post.likes_count = actual_likes_count
                    updated_count += 1
            
            # 提交更改
            if updated_count > 0:
                db.session.commit()
                print(f"成功修正 {updated_count} 条帖子的点赞数")
            else:
                print("所有帖子的点赞数都正确，无需修改")
                
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"修复点赞数据时出错: {str(e)}")
            return False

if __name__ == '__main__':
    fix_community_likes() 