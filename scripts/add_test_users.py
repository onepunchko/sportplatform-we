#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
添加测试用户数据
用于开发和测试阶段，生成一些用户数据
"""

import sys
import os
import random
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, UserPreference

def add_test_users():
    """添加测试用户数据"""
    print("开始添加测试用户数据...")
    
    # 检查是否已有用户数据
    existing_users = User.query.count()
    if existing_users > 0:
        print(f"数据库中已有 {existing_users} 个用户，跳过添加")
        return True
    
    # 用户数据
    test_users = [
        {
            'username': 'test_user1',
            'password': '123456',
            'nickname': '李明',
            'avatar': '/static/images/avatars/avatar1.png',
            'gender': 1,  # 男
            'age': 22,
            'height': 178.5,
            'weight': 70.2,
            'phone_number': '13800138001',
            'preferences': ['跑步', '篮球']
        },
        {
            'username': 'test_user2',
            'password': '123456',
            'nickname': '王琳',
            'avatar': '/static/images/avatars/avatar2.png',
            'gender': 0,  # 女
            'age': 20,
            'height': 165.0,
            'weight': 52.0,
            'phone_number': '13800138002',
            'preferences': ['游泳', '瑜伽']
        },
        {
            'username': 'test_user3',
            'password': '123456',
            'nickname': '张华',
            'avatar': '/static/images/avatars/avatar3.png',
            'gender': 1,  # 男
            'age': 25,
            'height': 182.0,
            'weight': 75.5,
            'phone_number': '13800138003',
            'preferences': ['健身', '足球']
        },
        {
            'username': 'test_user4',
            'password': '123456',
            'nickname': '刘芳',
            'avatar': '/static/images/avatars/avatar4.png',
            'gender': 0,  # 女
            'age': 21,
            'height': 160.0,
            'weight': 50.0,
            'phone_number': '13800138004',
            'preferences': ['羽毛球', '跑步']
        },
        {
            'username': 'test_user5',
            'password': '123456',
            'nickname': '赵强',
            'avatar': '/static/images/avatars/avatar5.png',
            'gender': 1,  # 男
            'age': 24,
            'height': 175.0,
            'weight': 68.0,
            'phone_number': '13800138005',
            'preferences': ['篮球', '健身']
        }
    ]
    
    # 添加用户数据
    for user_data in test_users:
        # 创建用户
        user = User(
            username=user_data['username'],
            nickname=user_data['nickname'],
            avatar=user_data['avatar'],
            gender=user_data['gender'],
            age=user_data['age'],
            height=user_data['height'],
            weight=user_data['weight'],
            phone_number=user_data['phone_number'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        user.password = user_data['password']  # 设置密码，会自动加密
        
        db.session.add(user)
        db.session.flush()  # 获取用户ID
        
        # 添加用户偏好
        for preference in user_data['preferences']:
            user_preference = UserPreference(
                user_id=user.id,
                preference=preference
            )
            db.session.add(user_preference)
    
    # 提交事务
    db.session.commit()
    
    print(f"成功添加了 {len(test_users)} 个测试用户")
    return True

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        add_test_users() 