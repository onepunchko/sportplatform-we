#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加社区模拟数据
用于开发和测试阶段，生成一些社区帖子数据
"""

import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, CommunityPost, PostLike, PostComment

def add_mock_community_data():
    """添加社区模拟数据"""
    print("开始添加社区模拟数据...")
    
    # 查找数据库中的用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先添加用户数据")
        return False
    
    # 删除现有的帖子数据(可选)
    # db.session.query(PostLike).delete()
    # db.session.query(PostComment).delete()
    # db.session.query(CommunityPost).delete()
    # db.session.commit()
    
    # 检查是否已有帖子数据
    existing_posts = CommunityPost.query.count()
    if existing_posts > 0:
        print(f"数据库中已有 {existing_posts} 条帖子数据，跳过添加")
        return True
    
    # 帖子内容模板
    post_templates = [
        "今天完成了{distance}公里的跑步，感觉很棒！#运动健康 #跑步",
        "在{location}打了2小时篮球，球技有进步！#篮球 #运动",
        "分享一下今天的健身计划：{workout}。坚持就是胜利！#健身 #坚持",
        "今天尝试了{activity}，很有挑战性但也很有趣！推荐大家尝试。",
        "记录一下训练成果，现在可以连续游{distance}米不休息了，加油！#游泳",
        "和朋友一起去{location}打羽毛球，超级开心！#羽毛球 #朋友",
        "分享一个我最近在用的训练app：{app}，功能很全面，推荐给大家。",
        "今天的{weather}天气很适合户外运动，完成了{activity}，状态不错！",
        "终于达成了连续运动{days}天的小目标，继续加油！#坚持 #目标",
        "最近在学习{skill}，进步显著，想找到志同道合的朋友一起练习。"
    ]
    
    # 运动地点
    locations = ["大学体育馆", "西区操场", "健身中心", "游泳馆", "篮球场", "田径场", "羽毛球馆", "社区公园"]
    
    # 运动类型
    activities = ["跑步", "篮球", "足球", "羽毛球", "乒乓球", "游泳", "健身", "瑜伽", "攀岩", "骑行"]
    
    # 健身内容
    workouts = [
        "胸肌训练 + HIIT 30分钟",
        "背部肌群 + 10公里跑步",
        "腿部训练日 + 拉伸",
        "全身有氧 45分钟",
        "核心力量 + 柔韧性训练",
        "手臂训练 + 5公里跑步"
    ]
    
    # 运动APP
    apps = ["Keep", "咕咚", "悦跑圈", "Nike Run Club", "Strava", "adidas Running", "小米运动"]
    
    # 天气
    weathers = ["晴朗", "多云", "微风", "凉爽", "温暖", "舒适"]
    
    # 运动技能
    skills = ["游泳自由泳", "篮球投篮", "网球发球", "瑜伽倒立", "健身计划制定", "长跑配速控制", "足球盘带"]
    
    # 创建模拟帖子
    posts_to_add = []
    current_time = datetime.now()
    
    for i in range(50):  # 创建50条帖子
        # 随机选择一个用户
        user = random.choice(users)
        
        # 创建帖子内容
        template = random.choice(post_templates)
        content = template.format(
            distance=random.randint(3, 20),
            location=random.choice(locations),
            workout=random.choice(workouts),
            activity=random.choice(activities),
            app=random.choice(apps),
            weather=random.choice(weathers),
            days=random.randint(7, 100),
            skill=random.choice(skills)
        )
        
        # 创建发布时间，越新的帖子越接近当前时间
        hours_ago = int((50 - i) * 5 * random.random())
        post_time = current_time - timedelta(hours=hours_ago)
        
        # 随机图片数量
        image_count = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]
        images = []
        for j in range(image_count):
            img_id = random.randint(1, 10)
            images.append(f"/static/images/posts/post{img_id}.jpg")
        
        # 创建帖子对象
        post = CommunityPost(
            user_id=user.id,
            type=random.choice(activities).lower(),
            content=content,
            images=str(images) if images else None,
            likes_count=0,  # 初始点赞数为0
            created_at=post_time
        )
        
        posts_to_add.append(post)
    
    # 批量添加帖子
    db.session.add_all(posts_to_add)
    db.session.commit()
    
    print(f"成功添加了 {len(posts_to_add)} 条社区帖子数据")
    
    # 添加评论和点赞
    print("正在添加评论和点赞数据...")
    all_posts = CommunityPost.query.all()
    comments_added = 0
    likes_added = 0
    
    # 评论模板
    comment_templates = [
        "加油，继续保持！",
        "厉害了，这个成绩很棒！",
        "我也想尝试一下，看起来很有趣",
        "请问你用的什么装备？推荐一下",
        "最近我也在练习这个，找个时间一起吧",
        "感谢分享，很有帮助",
        "这个地方我也去过，环境确实不错",
        "你的进步很大，有什么秘诀吗？",
        "坚持就是胜利，继续加油！",
        "这个训练方式很科学，我也试试"
    ]
    
    for post in all_posts:
        # 为每个帖子添加随机数量的评论
        comment_count = random.randint(0, 8)
        for i in range(comment_count):
            # 随机选择一个用户发表评论
            commenter = random.choice(users)
            
            # 避免自己评论自己的帖子
            if commenter.id == post.user_id and random.random() < 0.7:
                continue
                
            # 创建评论时间，晚于帖子发布时间
            hours_after_post = random.randint(0, int((current_time - post.created_at).total_seconds() / 3600))
            comment_time = post.created_at + timedelta(hours=hours_after_post)
            
            # 创建评论
            comment = PostComment(
                post_id=post.id,
                user_id=commenter.id,
                content=random.choice(comment_templates),
                created_at=comment_time
            )
            
            db.session.add(comment)
            comments_added += 1
        
        # 为每个帖子添加随机数量的点赞
        like_count = random.randint(0, 15)
        likers = random.sample(users, min(like_count, len(users)))
        
        for liker in likers:
            # 创建点赞时间，晚于帖子发布时间
            hours_after_post = random.randint(0, int((current_time - post.created_at).total_seconds() / 3600))
            like_time = post.created_at + timedelta(hours=hours_after_post)
            
            # 创建点赞
            like = PostLike(
                post_id=post.id,
                user_id=liker.id,
                created_at=like_time
            )
            
            db.session.add(like)
            likes_added += 1
        
        # 更新帖子的点赞数
        post.likes_count = like_count
    
    db.session.commit()
    
    print(f"成功添加了 {comments_added} 条评论和 {likes_added} 个点赞")
    return True

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        add_mock_community_data() 