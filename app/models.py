from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

# 用户表
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    nickname = db.Column(db.String(64))
    avatar = db.Column(db.String(256))
    gender = db.Column(db.Integer, default=0)  # 0-女，1-男
    age = db.Column(db.Integer)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    # 微信登录相关字段
    openid = db.Column(db.String(64), unique=True, index=True)
    unionid = db.Column(db.String(64), index=True)
    session_key = db.Column(db.String(128))
    phone_number = db.Column(db.String(32))
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 用户与运动记录的关系
    sport_records = db.relationship('SportRecord', backref='user', lazy='dynamic')
    
    # 用户与运动目标的关系
    sport_goals = db.relationship('SportGoal', backref='user', lazy='dynamic')
    
    # 用户与运动偏好的关系
    preferences = db.relationship('UserPreference', backref='user', lazy='dynamic')
    
    # 用户与场地预约的关系
    reservations = db.relationship('VenueReservation', backref='user', lazy='dynamic')
    
    # 用户与社区帖子的关系
    posts = db.relationship('CommunityPost', backref='user', lazy='dynamic')
    comments = db.relationship('PostComment', backref='user', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
        
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        preference_list = [p.preference for p in self.preferences.all()]
        return {
            'userId': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'gender': self.gender,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            'phoneNumber': self.phone_number,
            'preference': preference_list
        }

# 用户运动偏好表
class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    preference = db.Column(db.String(64))  # 运动偏好类型

# 资讯分类表
class NewsCategory(db.Model):
    __tablename__ = 'news_categories'
    
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(64))
    
    # 分类与资讯的关系
    news = db.relationship('News', backref='category', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }

# 资讯表
class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    content = db.Column(db.Text)
    image = db.Column(db.String(256))
    source = db.Column(db.String(64))
    author = db.Column(db.String(64))
    views = db.Column(db.Integer, default=0)
    category_id = db.Column(db.String(32), db.ForeignKey('news_categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self, detail=False):
        result = {
            'id': self.id,
            'title': self.title,
            'image': self.image,
            'source': self.source,
            'date': self.created_at.strftime('%Y-%m-%d'),
            'views': self.views,
            'content': self.content[:100] if not detail else self.content
        }
        
        if detail:
            result.update({
                'author': self.author,
                'publishTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return result

# 运动记录表
class SportRecord(db.Model):
    __tablename__ = 'sport_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(32))  # 运动类型
    distance = db.Column(db.Float)  # 运动距离（米）
    duration = db.Column(db.Integer)  # 运动时长（秒）
    calories = db.Column(db.Float)  # 消耗卡路里
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    avg_pace = db.Column(db.String(16))  # 平均配速
    route = db.Column(db.Text)  # 运动轨迹，JSON格式
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'distance': self.distance,
            'duration': self.duration,
            'calories': self.calories,
            'startTime': self.start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'endTime': self.end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'avgPace': self.avg_pace,
            'route': self.route
        }

# 运动目标表
class SportGoal(db.Model):
    __tablename__ = 'sport_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    daily_steps = db.Column(db.Integer)  # 每日步数目标
    daily_distance = db.Column(db.Float)  # 每日距离目标（公里）
    daily_calories = db.Column(db.Float)  # 每日消耗卡路里目标
    weekly_frequency = db.Column(db.Integer)  # 每周运动频次目标
    weekly_duration = db.Column(db.Integer)  # 每周运动时长目标（分钟）
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def to_dict(self):
        return {
            'daily': {
                'steps': self.daily_steps,
                'distance': self.daily_distance,
                'calories': self.daily_calories
            },
            'weekly': {
                'frequency': self.weekly_frequency,
                'duration': self.weekly_duration
            }
        }

# 运动挑战表
class SportChallenge(db.Model):
    __tablename__ = 'sport_challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    goal_type = db.Column(db.String(32))  # 目标类型
    goal_value = db.Column(db.Float)  # 目标值
    reward_points = db.Column(db.Integer)  # 奖励积分
    reward_badge = db.Column(db.String(32))  # 奖励徽章
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 运动挑战与用户参与的关系
    participants = db.relationship('ChallengeParticipant', backref='challenge', lazy='dynamic')
    
    def to_dict(self, user_id=None):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'startDate': self.start_date.strftime('%Y-%m-%d'),
            'endDate': self.end_date.strftime('%Y-%m-%d'),
            'goal': {
                'type': self.goal_type,
                'value': self.goal_value
            },
            'reward': {
                'points': self.reward_points,
                'badge': self.reward_badge
            },
            'participants': self.participants.count()
        }
        
        # 如果提供了用户ID，查询该用户的参与状态和进度
        if user_id:
            participant = self.participants.filter_by(user_id=user_id).first()
            result['isJoined'] = participant is not None
            result['progress'] = participant.progress if participant else 0
            
        return result

# 运动挑战参与表
class ChallengeParticipant(db.Model):
    __tablename__ = 'challenge_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('sport_challenges.id'))
    join_date = db.Column(db.Date)
    progress = db.Column(db.Float, default=0)  # 完成进度（百分比）
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 添加用户关系
    user = db.relationship('User', backref=db.backref('challenges', lazy='dynamic'))

# 场地表
class Venue(db.Model):
    __tablename__ = 'venues'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    type = db.Column(db.String(32))
    location = db.Column(db.String(256))
    description = db.Column(db.Text)
    image = db.Column(db.String(256))
    images = db.Column(db.Text)  # 多张图片，JSON格式
    capacity = db.Column(db.Integer)
    open_time = db.Column(db.String(16))
    close_time = db.Column(db.String(16))
    price = db.Column(db.Float)
    facilities = db.Column(db.Text)  # 场地设施，JSON格式
    rules = db.Column(db.Text)  # It's gonna use JSON format
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 场地与预约的关系
    reservations = db.relationship('VenueReservation', backref='venue', lazy='dynamic')
    
    # 场地与评价的关系
    reviews = db.relationship('VenueReview', backref='venue', lazy='dynamic')
    
    # 场地与时段的关系
    timeslots = db.relationship('VenueTimeSlot', backref='venue', lazy='dynamic')
    
    def to_dict(self, with_availability=False, date=None):
        result = {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'location': self.location,
            'image': self.image,
            'capacity': self.capacity,
            'openTime': self.open_time,
            'closeTime': self.close_time,
            'price': self.price,
            'rating': self.get_average_rating()
        }
        
        # 如果需要返回可用性信息
        if with_availability and date:
            result['available'] = self.has_available_timeslots(date)
            
        return result
    
    def get_average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0
        total = sum(review.rating for review in reviews)
        return round(total / len(reviews), 1)
    
    def has_available_timeslots(self, date):
        """检查指定日期是否有可用时段"""
        for timeslot in self.timeslots:
            # 检查时段是否可用
            reservations = VenueReservation.query.filter_by(
                venue_id=self.id,
                date=date,
                timeslot_id=timeslot.id
            ).all()
            
            if not reservations:
                return True
        return False

# 场地时段表
class VenueTimeSlot(db.Model):
    __tablename__ = 'venue_timeslots'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    start_time = db.Column(db.String(16))
    end_time = db.Column(db.String(16))
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self, date=None):
        result = {
            'id': self.id,
            'startTime': self.start_time,
            'endTime': self.end_time,
            'price': self.price
        }
        
        # 如果提供了日期，检查该时段是否可用
        if date:
            reservations = VenueReservation.query.filter_by(
                venue_id=self.venue_id,
                date=date,
                timeslot_id=self.id
            ).all()
            
            result['available'] = len(reservations) == 0
            
        return result

# 场地预约表
class VenueReservation(db.Model):
    __tablename__ = 'venue_reservations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    timeslot_id = db.Column(db.Integer, db.ForeignKey('venue_timeslots.id'))
    date = db.Column(db.Date)
    participants = db.Column(db.Integer)
    remark = db.Column(db.String(256))
    status = db.Column(db.String(16), default='pending')  # pending, confirmed, cancelled, completed
    price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.now)
    cancelled_at = db.Column(db.DateTime, nullable=True)  # 取消时间
    
    # 添加时段关系
    timeslot = db.relationship('VenueTimeSlot')
    
    def to_dict(self):
        return {
            'id': self.id,
            'venueId': self.venue_id,
            'venueName': self.venue.name,
            'venueImage': self.venue.image,
            'date': self.date.strftime('%Y-%m-%d'),
            'startTime': self.timeslot.start_time,
            'endTime': self.timeslot.end_time,
            'status': self.status,
            'price': self.price,
            'participants': self.participants,
            'createTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'cancelTime': self.cancelled_at.strftime('%Y-%m-%d %H:%M:%S') if self.cancelled_at else None
        }

# 场地评价表
class VenueReview(db.Model):
    __tablename__ = 'venue_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    rating = db.Column(db.Integer)  # 1-5星
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 添加用户关系
    user = db.relationship('User')
    
    def to_dict(self):
        return {
            'userId': self.user_id,
            'nickname': self.user.nickname,
            'avatar': self.user.avatar,
            'rating': self.rating,
            'comment': self.comment,
            'createTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 社区帖子表
class CommunityPost(db.Model):
    __tablename__ = 'community_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(32))  # 帖子类型
    content = db.Column(db.Text)
    images = db.Column(db.Text)  # 图片列表，JSON格式
    sport_record_id = db.Column(db.Integer, db.ForeignKey('sport_records.id'), nullable=True)
    likes_count = db.Column(db.Integer, default=0)  # 点赞数，与API保持一致
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 帖子与评论的关系
    comments = db.relationship('PostComment', backref='post', lazy='dynamic')
    
    # 帖子与运动记录的关系
    sport_record = db.relationship('SportRecord')
    
    # 帖子与点赞的关系
    user_likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    
    def to_dict(self, user_id=None):
        result = {
            'id': self.id,
            'userId': self.user_id,
            'nickname': self.user.nickname,
            'avatar': self.user.avatar,
            'type': self.type,
            'content': self.content,
            'images': self.images,
            'likes': self.likes_count,  # 返回likes字段以保持前端兼容性
            'comments': self.comments.count(),
            'createTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 如果存在关联的运动记录
        if self.sport_record_id:
            result['sportRecord'] = self.sport_record.to_dict()
            
        # 如果提供了用户ID，检查该用户是否点赞
        if user_id:
            like = PostLike.query.filter_by(post_id=self.id, user_id=user_id).first()
            result['isLiked'] = like is not None
            
        return result

# 帖子评论表
class PostComment(db.Model):
    __tablename__ = 'post_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'nickname': self.user.nickname,
            'avatar': self.user.avatar,
            'content': self.content,
            'createTime': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 帖子点赞表
class PostLike(db.Model):
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_posts.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # 添加用户关系
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'))

# AI教练聊天记录表
class AIChatHistory(db.Model):
    __tablename__ = 'ai_chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(16))  # user或ai
    content = db.Column(db.Text)
    suggestions = db.Column(db.Text, nullable=True)  # 建议的后续问题，JSON格式
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'timestamp': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# AI推荐的运动计划表
class AITrainingPlan(db.Model):
    __tablename__ = 'ai_training_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128))
    description = db.Column(db.Text)
    duration = db.Column(db.Integer)  # 计划持续时间（天）
    weekly_plan = db.Column(db.Text)  # 周计划，JSON格式
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        import json
        return {
            'planId': self.id,
            'name': self.name,
            'description': self.description,
            'duration': self.duration,
            'weeklyPlan': json.loads(self.weekly_plan)
        } 