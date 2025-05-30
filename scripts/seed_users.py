import sys
import os
import random
from datetime import datetime, timedelta
import json

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, UserPreference

def seed_users():
    """添加用户模拟数据"""
    print("开始添加用户模拟数据...")
    
    # 创建主要用户
    main_users = [
        {
            'username': 'user1',
            'password': 'password123',
            'nickname': '李明',
            'avatar': '/static/images/avatars/avatar1.png',
            'gender': 1,
            'age': 20,
            'height': 175.5,
            'weight': 68.5,
            'phone_number': '13800138001'
        },
        {
            'username': 'user2',
            'password': 'password123',
            'nickname': '王琳',
            'avatar': '/static/images/avatars/avatar2.png',
            'gender': 0,
            'age': 19,
            'height': 165.0,
            'weight': 52.0,
            'phone_number': '13800138002'
        },
        {
            'username': 'user3',
            'password': 'password123',
            'nickname': '张华',
            'avatar': '/static/images/avatars/avatar3.png',
            'gender': 1,
            'age': 21,
            'height': 180.0,
            'weight': 75.0,
            'phone_number': '13800138003'
        },
        {
            'username': 'user4',
            'password': 'password123',
            'nickname': '刘芳',
            'avatar': '/static/images/avatars/avatar4.png',
            'gender': 0,
            'age': 20,
            'height': 162.5,
            'weight': 50.0,
            'phone_number': '13800138004'
        },
        {
            'username': 'user5',
            'password': 'password123',
            'nickname': '赵强',
            'avatar': '/static/images/avatars/avatar5.png',
            'gender': 1,
            'age': 22,
            'height': 178.0,
            'weight': 72.0,
            'phone_number': '13800138005'
        }
    ]
    
    for user_data in main_users:
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"用户 {user_data['username']} 已存在，跳过创建")
            continue
            
        user = User(
            username=user_data['username'],
            nickname=user_data['nickname'],
            avatar=user_data['avatar'],
            gender=user_data['gender'],
            age=user_data['age'],
            height=user_data['height'],
            weight=user_data['weight'],
            phone_number=user_data['phone_number'],
            created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            last_login_at=datetime.now() - timedelta(hours=random.randint(1, 24))
        )
        user.password = user_data['password']
        db.session.add(user)
    
    # 提交以获取用户ID
    db.session.commit()
    
    # 添加运动偏好
    sport_preferences = ['跑步', '游泳', '篮球', '足球', '排球', '羽毛球', '网球', '乒乓球', '健身', '瑜伽']
    users = User.query.all()
    
    for user in users:
        # 每个用户随机选择1-3个运动偏好
        num_preferences = random.randint(1, 3)
        selected_preferences = random.sample(sport_preferences, num_preferences)
        
        for preference in selected_preferences:
            # 检查偏好是否已存在
            existing_preference = UserPreference.query.filter_by(user_id=user.id, preference=preference).first()
            if existing_preference:
                continue
                
            user_preference = UserPreference(
                user_id=user.id,
                preference=preference
            )
            db.session.add(user_preference)
    
    db.session.commit()
    print(f"成功添加了 {len(users)} 名用户和他们的运动偏好")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_users() 