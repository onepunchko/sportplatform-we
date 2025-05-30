from flask import Blueprint, request, jsonify, g
from ..models import SportRecord, SportGoal, SportChallenge, ChallengeParticipant
from ..utils import token_required, parse_json
from .. import db
from datetime import datetime, date, timedelta
import json

sport_bp = Blueprint('sport', __name__)

@sport_bp.route('/list', methods=['POST'])
@token_required
def get_sport_list():
    """获取运动记录列表"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 获取请求参数
    page = data.get('page', 1)
    page_size = data.get('pageSize', 10)
    sport_type = data.get('type')
    
    # 查询运动记录
    query = SportRecord.query.filter_by(user_id=user.id)
    
    # 按运动类型筛选
    if sport_type:
        query = query.filter_by(type=sport_type)
        
    # 按时间倒序排序
    query = query.order_by(SportRecord.start_time.desc())
    
    # 分页查询
    pagination = query.paginate(
        page=page, per_page=page_size, error_out=False)
    
    # 转换为JSON格式
    records = pagination.items
    result = {
        'total': pagination.total,
        'list': [record.to_dict() for record in records]
    }
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@sport_bp.route('/tracking', methods=['POST'])
@token_required
def get_sport_tracking():
    """获取运动追踪数据"""
    # 实际应用中，这里需要从数据库或缓存中获取用户的实时运动追踪数据
    # 这里只是一个示例实现
    
    # 假设用户没有正在进行的运动
    return jsonify({
        'error': 0,
        'body': {
            'isTracking': False,
            'sessionId': None,
            'type': None,
            'startTime': None,
            'duration': 0,
            'distance': 0,
            'calories': 0,
            'currentPace': None,
            'avgPace': None,
            'currentLocation': None,
            'route': []
        },
        'message': ''
    })

@sport_bp.route('/upload', methods=['POST'])
@token_required
def upload_sport_data():
    """上传运动数据"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 验证必填参数
    required_fields = ['type', 'distance', 'duration', 'calories', 'startTime', 'endTime']
    for field in required_fields:
        if field not in data:
            return jsonify({
                'error': 1,
                'body': None,
                'message': f'{field}参数不能为空'
            })
    
    # 创建运动记录
    record = SportRecord(
        user_id=user.id,
        type=data['type'],
        distance=data['distance'],
        duration=data['duration'],
        calories=data['calories'],
        start_time=datetime.strptime(data['startTime'], '%Y-%m-%d %H:%M:%S'),
        end_time=datetime.strptime(data['endTime'], '%Y-%m-%d %H:%M:%S'),
        avg_pace=data.get('avgPace'),
        route=json.dumps(data.get('route', []))
    )
    
    # 保存到数据库
    db.session.add(record)
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'recordId': record.id,
            'success': True
        },
        'message': ''
    })

@sport_bp.route('/goal', methods=['POST'])
@token_required
def get_sport_goal():
    """获取运动目标"""
    user = g.current_user
    
    # 查询用户的运动目标
    goal = SportGoal.query.filter_by(user_id=user.id).first()
    
    if not goal:
        # 如果用户没有设置目标，返回默认值
        return jsonify({
            'error': 0,
            'body': {
                'daily': {
                    'steps': 10000,
                    'distance': 5,
                    'calories': 300
                },
                'weekly': {
                    'frequency': 3,
                    'duration': 150
                },
                'progress': {
                    'dailySteps': 0,
                    'dailyDistance': 0,
                    'dailyCalories': 0,
                    'weeklyFrequency': 0,
                    'weeklyDuration': 0
                }
            },
            'message': ''
        })
    
    # 计算当日和本周的进度
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    
    # 计算本周的起始日期
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    
    # 查询当日的运动记录
    today_records = SportRecord.query.filter(
        SportRecord.user_id == user.id,
        SportRecord.start_time >= today_start,
        SportRecord.start_time < today_end
    ).all()
    
    # 查询本周的运动记录
    week_records = SportRecord.query.filter(
        SportRecord.user_id == user.id,
        SportRecord.start_time >= week_start,
        SportRecord.start_time < week_end
    ).all()
    
    # 计算当日进度
    daily_steps = sum(record.distance / 0.7 for record in today_records)  # 假设每步0.7米
    daily_distance = sum(record.distance for record in today_records) / 1000  # 转换为公里
    daily_calories = sum(record.calories for record in today_records)
    
    # 计算本周进度
    weekly_frequency = len(set(record.start_time.date() for record in week_records))
    weekly_duration = sum(record.duration for record in week_records) / 60  # 转换为分钟
    
    result = {
        'daily': goal.to_dict()['daily'],
        'weekly': goal.to_dict()['weekly'],
        'progress': {
            'dailySteps': int(daily_steps),
            'dailyDistance': daily_distance,
            'dailyCalories': daily_calories,
            'weeklyFrequency': weekly_frequency,
            'weeklyDuration': weekly_duration
        }
    }
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@sport_bp.route('/goal/set', methods=['POST'])
@token_required
def set_sport_goal():
    """设置运动目标"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 查询用户是否已有运动目标
    goal = SportGoal.query.filter_by(user_id=user.id).first()
    
    if not goal:
        # 创建新的运动目标
        goal = SportGoal(user_id=user.id)
    
    # 获取日常目标
    daily = data.get('daily', {})
    if daily:
        goal.daily_steps = daily.get('steps', goal.daily_steps)
        goal.daily_distance = daily.get('distance', goal.daily_distance)
        goal.daily_calories = daily.get('calories', goal.daily_calories)
    
    # 获取每周目标
    weekly = data.get('weekly', {})
    if weekly:
        goal.weekly_frequency = weekly.get('frequency', goal.weekly_frequency)
        goal.weekly_duration = weekly.get('duration', goal.weekly_duration)
    
    # 保存到数据库
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'success': True
        },
        'message': ''
    })

@sport_bp.route('/challenge/list', methods=['POST'])
@token_required
def get_challenge_list():
    """获取运动挑战列表"""
    user = g.current_user
    
    # 查询所有运动挑战
    challenges = SportChallenge.query.filter(
        SportChallenge.end_date >= date.today()
    ).order_by(SportChallenge.start_date.asc()).all()
    
    # 转换为JSON格式
    result = [challenge.to_dict(user_id=user.id) for challenge in challenges]
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@sport_bp.route('/challenge/join', methods=['POST'])
@token_required
def join_challenge():
    """参加运动挑战"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 获取挑战ID
    challenge_id = data.get('id')
    
    if not challenge_id:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '挑战ID不能为空'
        })
    
    # 查询挑战
    challenge = SportChallenge.query.get(challenge_id)
    
    if not challenge:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '挑战不存在'
        })
    
    # 检查用户是否已参加该挑战
    participant = ChallengeParticipant.query.filter_by(
        user_id=user.id, challenge_id=challenge_id
    ).first()
    
    if participant:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '您已参加该挑战'
        })
    
    # 创建参与记录
    participant = ChallengeParticipant(
        user_id=user.id,
        challenge_id=challenge_id,
        join_date=date.today(),
        progress=0,
        is_completed=False
    )
    
    # 保存到数据库
    db.session.add(participant)
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'success': True,
            'challengeId': challenge_id
        },
        'message': ''
    }) 