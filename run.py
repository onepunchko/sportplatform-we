import os
from app import create_app, db
from app.models import User, UserPreference, News, NewsCategory
from app.models import SportRecord, SportGoal, SportChallenge, ChallengeParticipant
from app.models import Venue, VenueTimeSlot, VenueReservation, VenueReview
from app.models import CommunityPost, PostComment, PostLike
from app.models import AIChatHistory, AITrainingPlan
from flask_migrate import Migrate
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取环境配置
flask_env = os.getenv('FLASK_ENV', 'development')
host = os.getenv('HOST', '127.0.0.1')
port = int(os.getenv('PORT', 5000))
debug = os.getenv('DEBUG', 'True').lower() in ('true', '1', 't')

# 创建应用实例
app = create_app(flask_env)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    """为Flask shell自动导入对象"""
    return {
        'db': db,
        'User': User,
        'UserPreference': UserPreference,
        'News': News,
        'NewsCategory': NewsCategory,
        'SportRecord': SportRecord,
        'SportGoal': SportGoal,
        'SportChallenge': SportChallenge,
        'ChallengeParticipant': ChallengeParticipant,
        'Venue': Venue,
        'VenueTimeSlot': VenueTimeSlot,
        'VenueReservation': VenueReservation,
        'VenueReview': VenueReview,
        'CommunityPost': CommunityPost,
        'PostComment': PostComment,
        'PostLike': PostLike,
        'AIChatHistory': AIChatHistory,
        'AITrainingPlan': AITrainingPlan
    }

if __name__ == '__main__':
    # 显示当前环境
    print(f"Running in {flask_env.upper()} mode")
    app.run(host=host, port=port, debug=debug) 