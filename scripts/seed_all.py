import sys
import os
import time

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from scripts.seed_users import seed_users
from scripts.seed_news import seed_news
from scripts.seed_sport_records import seed_sport_records
from scripts.seed_sport_goals import seed_sport_goals
from scripts.seed_venues import seed_venues
from scripts.seed_challenges import seed_challenges
from scripts.seed_community import seed_community
from scripts.seed_ai_data import seed_ai_data

def seed_all():
    """按顺序填充所有表的模拟数据"""
    print("=" * 50)
    print("开始填充所有表的模拟数据")
    print("=" * 50)
    
    start_time = time.time()
    
    # 按照依赖关系顺序执行各个数据填充函数
    seed_users()
    print("\n" + "-" * 50 + "\n")
    
    seed_news()
    print("\n" + "-" * 50 + "\n")
    
    seed_sport_records()
    print("\n" + "-" * 50 + "\n")
    
    seed_sport_goals()
    print("\n" + "-" * 50 + "\n")
    
    seed_venues()
    print("\n" + "-" * 50 + "\n")
    
    seed_challenges()
    print("\n" + "-" * 50 + "\n")
    
    seed_community()
    print("\n" + "-" * 50 + "\n")
    
    seed_ai_data()
    
    end_time = time.time()
    print("\n" + "=" * 50)
    print(f"所有数据填充完成，耗时 {end_time - start_time:.2f} 秒")
    print("=" * 50)

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_all() 