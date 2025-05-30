import sys
import os
import random
from datetime import datetime, timedelta, date

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, SportChallenge, ChallengeParticipant

def seed_challenges():
    """添加运动挑战模拟数据"""
    print("开始添加运动挑战模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 创建挑战
    challenges_data = [
        {
            'title': '30天跑步挑战',
            'description': '连续30天每天完成至少3公里跑步，培养跑步习惯，提升心肺功能。',
            'goal_type': 'distance',
            'goal_value': 90.0,  # 总距离90公里
            'reward_points': 500,
            'reward_badge': 'runner_badge'
        },
        {
            'title': '游泳达人挑战',
            'description': '两周内完成总计5000米的游泳距离，提升游泳技能和耐力。',
            'goal_type': 'distance',
            'goal_value': 5.0,  # 总距离5公里
            'reward_points': 300,
            'reward_badge': 'swimmer_badge'
        },
        {
            'title': '燃脂挑战',
            'description': '一个月内通过有氧运动消耗总计10000卡路里，达到减脂效果。',
            'goal_type': 'calories',
            'goal_value': 10000.0,
            'reward_points': 600,
            'reward_badge': 'fat_burner_badge'
        },
        {
            'title': '力量训练挑战',
            'description': '三周内完成15次力量训练，增强肌肉力量和耐力。',
            'goal_type': 'frequency',
            'goal_value': 15.0,
            'reward_points': 400,
            'reward_badge': 'strength_badge'
        },
        {
            'title': '晨练习惯养成',
            'description': '连续21天完成晨练，培养健康的生活习惯。',
            'goal_type': 'days',
            'goal_value': 21.0,
            'reward_points': 350,
            'reward_badge': 'early_bird_badge'
        }
    ]
    
    challenges_ids = []
    
    for challenge_data in challenges_data:
        # 检查挑战是否已存在
        existing_challenge = SportChallenge.query.filter_by(title=challenge_data['title']).first()
        if existing_challenge:
            challenges_ids.append(existing_challenge.id)
            print(f"挑战 '{challenge_data['title']}' 已存在，跳过创建")
            continue
        
        # 创建开始和结束日期
        today = date.today()
        # 随机决定挑战是否已经开始
        if random.random() > 0.5:  # 50%的挑战已经开始
            start_date = today - timedelta(days=random.randint(5, 15))
            duration = random.randint(21, 60)  # 挑战持续21-60天
        else:  # 50%的挑战还未开始
            start_date = today + timedelta(days=random.randint(1, 10))
            duration = random.randint(14, 45)  # 挑战持续14-45天
        
        end_date = start_date + timedelta(days=duration)
        
        challenge = SportChallenge(
            title=challenge_data['title'],
            description=challenge_data['description'],
            start_date=start_date,
            end_date=end_date,
            goal_type=challenge_data['goal_type'],
            goal_value=challenge_data['goal_value'],
            reward_points=challenge_data['reward_points'],
            reward_badge=challenge_data['reward_badge'],
            created_at=datetime.now() - timedelta(days=random.randint(20, 60))
        )
        
        db.session.add(challenge)
        db.session.flush()  # 获取ID
        challenges_ids.append(challenge.id)
    
    # 提交以获取挑战ID
    db.session.commit()
    
    # 添加参与记录
    participant_count = 0
    
    for challenge_id in challenges_ids:
        challenge = SportChallenge.query.get(challenge_id)
        
        # 如果挑战还未开始，参与人数较少
        max_participants = min(len(users), 8 if challenge.start_date > date.today() else 15)
        num_participants = random.randint(max(1, max_participants // 2), max_participants)
        
        # 随机选择参与用户
        participating_users = random.sample(users, num_participants)
        
        for user in participating_users:
            # 检查该用户是否已参与此挑战
            existing_participant = ChallengeParticipant.query.filter_by(
                user_id=user.id, 
                challenge_id=challenge_id
            ).first()
            
            if existing_participant:
                continue
            
            # 创建参与记录
            # 如果挑战已经开始，加入日期应该在开始日期之后
            if challenge.start_date <= date.today():
                join_date = max(challenge.start_date, (date.today() - timedelta(days=random.randint(0, (date.today() - challenge.start_date).days))))
            else:
                # 如果挑战还未开始，加入日期是当前日期
                join_date = date.today() - timedelta(days=random.randint(0, 5))
            
            # 计算进度
            if challenge.start_date <= date.today():
                # 如果挑战已经开始
                days_since_start = (date.today() - challenge.start_date).days
                total_days = (challenge.end_date - challenge.start_date).days
                
                # 根据已经过去的时间比例，计算进度
                time_progress = min(100, max(0, days_since_start / total_days * 100))
                
                # 进度应该根据时间比例有所波动
                # 有些用户进度较快，有些较慢
                progress_factor = random.uniform(0.7, 1.3)
                progress = min(100, max(0, time_progress * progress_factor))
            else:
                # 如果挑战还未开始，进度为0
                progress = 0
            
            # 是否已完成
            is_completed = progress >= 100
            
            participant = ChallengeParticipant(
                user_id=user.id,
                challenge_id=challenge_id,
                join_date=join_date,
                progress=progress,
                is_completed=is_completed,
                created_at=datetime.combine(join_date, datetime.min.time())
            )
            
            db.session.add(participant)
            participant_count += 1
    
    db.session.commit()
    print(f"成功创建了 {len(challenges_ids)} 个运动挑战和 {participant_count} 条参与记录")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_challenges() 