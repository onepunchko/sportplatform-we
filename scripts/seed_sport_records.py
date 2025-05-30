import sys
import os
import random
from datetime import datetime, timedelta
import json

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, SportRecord

def seed_sport_records():
    """添加运动记录模拟数据"""
    print("开始添加运动记录模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 运动类型和相关数据范围
    sport_types = {
        'running': {
            'distance_range': (2000, 10000),  # 单位：米
            'duration_range': (10*60, 60*60),  # 单位：秒
            'calories_range': (100, 500),
            'pace_fn': lambda dist, dur: f"{int(dur/60/dist*1000)}'{int((dur/60/dist*1000 % 1) * 60)}\""
        },
        'swimming': {
            'distance_range': (500, 2000),
            'duration_range': (15*60, 60*60),
            'calories_range': (200, 600),
            'pace_fn': lambda dist, dur: f"{int(dur/60/(dist/100))}'{int((dur/60/(dist/100) % 1) * 60)}\"/100m"
        },
        'cycling': {
            'distance_range': (5000, 30000),
            'duration_range': (20*60, 120*60),
            'calories_range': (200, 800),
            'pace_fn': lambda dist, dur: f"{round(dist/1000/(dur/3600), 1)} km/h"
        },
        'basketball': {
            'distance_range': (2000, 5000),
            'duration_range': (30*60, 120*60),
            'calories_range': (300, 700),
            'pace_fn': lambda dist, dur: "N/A"
        },
        'fitness': {
            'distance_range': (0, 0),
            'duration_range': (30*60, 90*60),
            'calories_range': (200, 600),
            'pace_fn': lambda dist, dur: "N/A"
        }
    }
    
    # 为每个用户生成运动记录
    record_count = 0
    for user in users:
        # 每个用户生成5-15条运动记录
        num_records = random.randint(5, 15)
        
        for i in range(num_records):
            # 随机选择一种运动类型
            sport_type = random.choice(list(sport_types.keys()))
            type_data = sport_types[sport_type]
            
            # 随机生成距离、时长和卡路里
            distance = random.randint(*type_data['distance_range']) if type_data['distance_range'][1] > 0 else 0
            duration = random.randint(*type_data['duration_range'])
            calories = random.randint(*type_data['calories_range'])
            
            # 生成平均配速
            avg_pace = type_data['pace_fn'](distance, duration) if distance > 0 else "N/A"
            
            # 生成时间，过去30天内
            end_time = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            start_time = end_time - timedelta(seconds=duration)
            
            # 生成运动轨迹数据（简单示例）
            route_data = []
            if distance > 0:
                # 简单模拟一些GPS点
                num_points = max(10, duration // 60)  # 每分钟至少一个点
                base_lat, base_lon = 39.9, 116.3  # 北京某处作为基础点
                
                for j in range(num_points):
                    lat = base_lat + (random.random() - 0.5) * 0.01
                    lon = base_lon + (random.random() - 0.5) * 0.01
                    route_data.append({
                        'lat': lat,
                        'lon': lon,
                        'timestamp': (start_time + timedelta(seconds=j * (duration / num_points))).timestamp()
                    })
            
            # 检查此用户在此时间段是否已有记录
            existing_record = SportRecord.query.filter_by(
                user_id=user.id,
                start_time=start_time
            ).first()
            
            if existing_record:
                # 跳过创建
                continue
            
            # 创建运动记录
            record = SportRecord(
                user_id=user.id,
                type=sport_type,
                distance=distance,
                duration=duration,
                calories=calories,
                start_time=start_time,
                end_time=end_time,
                avg_pace=avg_pace,
                route=json.dumps(route_data) if route_data else None,
                created_at=end_time
            )
            
            db.session.add(record)
            record_count += 1
    
    db.session.commit()
    print(f"成功添加了 {record_count} 条运动记录")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_sport_records() 