import sys
import os
import random
from datetime import datetime, timedelta
import json

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, CommunityPost, PostComment, PostLike, SportRecord

def seed_community():
    """添加社区相关模拟数据"""
    print("开始添加社区相关模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 获取所有运动记录
    sport_records = SportRecord.query.all()
    
    # 创建社区帖子
    post_types = ['running', 'basketball', 'fitness', 'swimming', 'football', 'badminton']
    
    post_contents = [
        "今天完成了5公里跑步，感觉很不错！#运动 #健康",
        "在体育馆打了两小时篮球，进步很大！#篮球",
        "分享一下今天的健身计划，希望对大家有帮助。#健身",
        "今天的游泳训练完成了2000米，新的个人记录！#游泳",
        "周末约了朋友踢足球，超级开心！#足球 #周末",
        "羽毛球训练课上学会了新技巧，感谢教练！#羽毛球",
        "慢跑结束，记录一下今天的心情，天气真好！#跑步 #心情",
        "健身房新添了器材，今天试了一下，效果不错！#健身 #新器材",
        "游泳真的是全身运动，游完感觉神清气爽！#游泳 #放松",
        "和同学一起打篮球，配合越来越默契了！#篮球 #团队",
        "尝试了HIIT训练，强度真的很大，但效果显著！#HIIT #挑战自我",
        "今天骑行20公里，沿途风景美不胜收！#骑行 #户外",
        "瑜伽课后感觉身体柔韧性提高了不少！#瑜伽 #柔韧",
        "第一次尝试攀岩，虽然手臂酸痛但很有成就感！#攀岩 #新尝试",
        "坚持晨跑一个月了，感觉整个人的精神状态好多了！#晨跑 #坚持"
    ]
    
    locations = ["大学体育馆", "校园跑道", "健身中心", "游泳馆", "篮球场", "足球场", None]
    
    image_paths = [
        "/static/images/posts/running1.jpg",
        "/static/images/posts/basketball1.jpg",
        "/static/images/posts/fitness1.jpg",
        "/static/images/posts/swimming1.jpg",
        "/static/images/posts/running2.jpg",
        "/static/images/posts/basketball2.jpg",
        None
    ]
    
    posts_count = 0
    
    # 为每个用户创建1-3条帖子
    for user in users:
        num_posts = random.randint(1, 3)
        
        for i in range(num_posts):
            post_type = random.choice(post_types)
            content = random.choice(post_contents)
            location = random.choice(locations)
            
            # 随机决定是否添加图片
            images = []
            if random.random() > 0.3:  # 70%的帖子有图片
                num_images = random.randint(1, 3)
                for j in range(num_images):
                    image_path = random.choice(image_paths)
                    if image_path:
                        images.append(image_path)
            
            # 随机决定是否关联运动记录
            sport_record_id = None
            if sport_records and random.random() > 0.7:  # 30%的帖子关联运动记录
                # 获取该用户的运动记录
                user_records = [r for r in sport_records if r.user_id == user.id]
                if user_records:
                    sport_record_id = random.choice(user_records).id
            
            # 创建时间（最近30天内）
            created_at = datetime.now() - timedelta(days=random.randint(0, 30), 
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59))
            
            # 创建帖子
            post = CommunityPost(
                user_id=user.id,
                type=post_type,
                content=content,
                images=json.dumps(images) if images else None,
                sport_record_id=sport_record_id,
                likes_count=0,  # 初始化为0，后面会更新
                created_at=created_at
            )
            
            db.session.add(post)
            posts_count += 1
    
    # 提交以获取帖子ID
    db.session.commit()
    print(f"成功创建了 {posts_count} 条社区帖子")
    
    # 获取所有帖子
    posts = CommunityPost.query.all()
    
    # 添加点赞和评论
    comments_count = 0
    likes_count = 0
    
    comment_templates = [
        "加油，继续保持！",
        "太棒了，我也想试试",
        "请问你是怎么坚持下来的？",
        "谢谢分享，很有帮助",
        "看起来很不错，有进步！",
        "请问是在哪个场馆健身的？环境看起来很好",
        "分享一下你的训练计划吧",
        "厉害了，我才刚开始练习",
        "这个姿势很标准，👍",
        "期待你的下一次分享！"
    ]
    
    for post in posts:
        # 为每条帖子添加2-8个点赞
        num_likes = random.randint(2, 8)
        liking_users = random.sample(users, min(num_likes, len(users)))
        
        for user in liking_users:
            # 确保用户没有给这条帖子点过赞
            existing_like = PostLike.query.filter_by(post_id=post.id, user_id=user.id).first()
            if existing_like:
                continue
                
            # 创建点赞
            like_time = post.created_at + timedelta(minutes=random.randint(5, 60*24))
            if like_time > datetime.now():
                like_time = datetime.now() - timedelta(minutes=random.randint(5, 60))
                
            like = PostLike(
                post_id=post.id,
                user_id=user.id,
                created_at=like_time
            )
            
            db.session.add(like)
            likes_count += 1
        
        # 为每条帖子添加0-5条评论
        num_comments = random.randint(0, 5)
        commenting_users = random.sample(users, min(num_comments, len(users)))
        
        for user in commenting_users:
            comment_time = post.created_at + timedelta(minutes=random.randint(5, 60*24))
            if comment_time > datetime.now():
                comment_time = datetime.now() - timedelta(minutes=random.randint(5, 60))
                
            comment = PostComment(
                post_id=post.id,
                user_id=user.id,
                content=random.choice(comment_templates),
                created_at=comment_time
            )
            
            db.session.add(comment)
            comments_count += 1
    
    # 更新帖子的点赞数
    for post in posts:
        post.likes_count = PostLike.query.filter_by(post_id=post.id).count()
    
    db.session.commit()
    print(f"成功添加了 {likes_count} 个点赞和 {comments_count} 条评论")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_community() 