from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
import sqlite3
import random
from datetime import datetime, timedelta

# 创建数据库实例
db = SQLAlchemy()

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    from .api.news import news_bp
    from .api.user import user_bp
    from .api.sport import sport_bp
    from .api.ai_coach import ai_coach_bp
    from .api.community import community_bp
    from .api.venue import venue_bp
    from .api.comment import comment_bp
    
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(sport_bp, url_prefix='/sport')
    app.register_blueprint(ai_coach_bp, url_prefix='/ai/coach')
    app.register_blueprint(community_bp, url_prefix='/community')
    app.register_blueprint(venue_bp, url_prefix='/venue')
    app.register_blueprint(comment_bp, url_prefix='/community')
    
    # 数据库初始化钩子
    with app.app_context():
        db.create_all()
        
        # 检查venue_reservations表是否存在cancelled_at字段，如果不存在则添加
        try:
            conn = sqlite3.connect(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
            cursor = conn.cursor()
            # 获取表结构
            cursor.execute("PRAGMA table_info(venue_reservations)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]
            
            # 如果cancelled_at字段不存在，则添加
            if 'cancelled_at' not in column_names:
                cursor.execute("ALTER TABLE venue_reservations ADD COLUMN cancelled_at TIMESTAMP")
                conn.commit()
                app.logger.info("已添加cancelled_at字段到venue_reservations表")
            
            cursor.close()
            conn.close()
        except Exception as e:
            app.logger.error(f"检查或添加cancelled_at字段时出错: {str(e)}")
            
        # 检查并添加社区模拟数据
        try:
            from .models import User, CommunityPost, PostComment, PostLike
            
            # 检查是否已有社区帖子数据
            posts_count = CommunityPost.query.count()
            if posts_count == 0:
                app.logger.info("正在添加社区模拟数据...")
                
                # 获取系统中的用户
                users = User.query.all()
                if not users:
                    app.logger.warning("数据库中没有用户数据，跳过添加社区模拟数据")
                    return app
                
                # 添加模拟帖子
                post_types = ['running', 'basketball', 'fitness', 'swimming', 'football', 'badminton']
                post_contents = [
                    "今天完成了5公里跑步，感觉很不错！#运动 #健康",
                    "在体育馆打了两小时篮球，进步很大！#篮球",
                    "分享一下今天的健身计划，希望对大家有帮助。#健身",
                    "今天的游泳训练完成了2000米，新的个人记录！#游泳",
                    "周末约了朋友踢足球，超级开心！#足球 #周末",
                    "羽毛球训练课上学会了新技巧，感谢教练！#羽毛球"
                ]
                
                # 创建5条模拟帖子
                for i in range(5):
                    post = CommunityPost(
                        user_id=random.choice(users).id,
                        type=random.choice(post_types),
                        content=random.choice(post_contents),
                        created_at=datetime.now() - timedelta(hours=random.randint(1, 48))
                    )
                    db.session.add(post)
                    
                db.session.commit()
                app.logger.info("成功添加社区模拟数据")
                
                # 添加一些模拟评论和点赞
                posts = CommunityPost.query.all()
                for post in posts:
                    # 添加1-3条评论
                    for _ in range(random.randint(1, 3)):
                        comment = PostComment(
                            post_id=post.id,
                            user_id=random.choice(users).id,
                            content=random.choice([
                                "加油，继续保持！",
                                "太棒了，我也想试试",
                                "请问你是怎么坚持下来的？",
                                "谢谢分享，很有帮助"
                            ]),
                            created_at=post.created_at + timedelta(minutes=random.randint(10, 300))
                        )
                        db.session.add(comment)
                    
                    # 添加2-5个点赞
                    for _ in range(random.randint(2, 5)):
                        like = PostLike(
                            post_id=post.id,
                            user_id=random.choice(users).id,
                            created_at=post.created_at + timedelta(minutes=random.randint(5, 200))
                        )
                        db.session.add(like)
                    
                    # 更新帖子点赞数
                    post.likes_count = PostLike.query.filter_by(post_id=post.id).count()
                
                db.session.commit()
                app.logger.info("成功添加社区评论和点赞数据")
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"添加社区模拟数据时出错: {str(e)}")
    
    return app 