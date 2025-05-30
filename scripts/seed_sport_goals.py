import sys
import os
import random
from datetime import datetime, timedelta

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, SportGoal

def seed_sport_goals():
    """添加运动目标模拟数据"""
    print("开始添加运动目标模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 为每个用户创建运动目标
    for user in users:
        # 检查用户是否已有运动目标
        existing_goal = SportGoal.query.filter_by(user_id=user.id).first()
        if existing_goal:
            print(f"用户 {user.username} 已有运动目标，跳过创建")
            continue
        
        # 根据用户信息生成合适的目标
        daily_steps = random.randint(6000, 12000)
        daily_distance = round(random.uniform(3.0, 8.0), 1)
        daily_calories = round(random.uniform(200.0, 500.0), 1)
        weekly_frequency = random.randint(3, 6)
        weekly_duration = weekly_frequency * random.randint(30, 90)
        
        goal = SportGoal(
            user_id=user.id,
            daily_steps=daily_steps,
            daily_distance=daily_distance,
            daily_calories=daily_calories,
            weekly_frequency=weekly_frequency,
            weekly_duration=weekly_duration,
            created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            updated_at=datetime.now() - timedelta(days=random.randint(0, 7))
        )
        
        db.session.add(goal)
    
    db.session.commit()
    print(f"成功为 {len(users)} 名用户添加了运动目标")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_sport_goals() 