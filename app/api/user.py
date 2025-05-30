from flask import Blueprint, request, jsonify, g, current_app
from ..models import User, UserPreference, SportRecord
from ..utils import token_required, generate_token
from .. import db
from datetime import datetime, timedelta
import json
import requests
import base64
from Crypto.Cipher import AES
import os
import uuid
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__)

# 允许的图片扩展名
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@user_bp.route('/login', methods=['POST'])
def login():
    """手机号登录"""
    data = request.get_json() or {}
    
    # 获取请求参数
    phone_number = data.get('phone')
    code = data.get('code')
    
    if not phone_number or not code:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '手机号和验证码不能为空'
        })
    
    # 检验验证码是否正确
    # 这里应该有验证码校验逻辑，简化处理
    if code != '123456' and code != '111111':
        return jsonify({
            'error': 1,
            'body': None,
            'message': '验证码错误'
        })
    
    # 查询用户
    user = User.query.filter_by(phone_number=phone_number).first()
    
    if not user:
        # 创建新用户
        user = User(
            phone_number=phone_number,
            username=f'phone_{phone_number[-6:]}',  # 使用手机号末尾6位作为用户名
            nickname=f'用户_{phone_number[-4:]}' # 使用手机号末尾4位作为昵称
        )
        db.session.add(user)
        db.session.commit()
    
    # 更新最后登录时间
    user.last_login_at = datetime.now()
    db.session.commit()
    
    # 生成token
    token, expire_time = generate_token(user.id)
    
    return jsonify({
        'error': 0,
        'body': {
            'token': token,
            'userId': user.id,
            'phoneNumber': phone_number,
            'nickname': user.nickname,
            'avatar': user.avatar,
            'expireTime': expire_time
        },
        'message': ''
    })

@user_bp.route('/wx-login', methods=['POST'])
def wx_login():
    """微信登录"""
    data = request.get_json() or {}
    
    # 获取请求参数
    code = data.get('code')
    
    if not code:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '微信授权码不能为空'
        })
    
    # 微信小程序配置
    app_id = current_app.config.get('WX_APP_ID')
    app_secret = current_app.config.get('WX_APP_SECRET')
    
    # 请求微信API获取openid和session_key
    url = f'https://api.weixin.qq.com/sns/jscode2session?appid={app_id}&secret={app_secret}&js_code={code}&grant_type=authorization_code'
    
    try:
        response = requests.get(url)
        result = response.json()
        
        if 'errcode' in result and result['errcode'] != 0:
            return jsonify({
                'error': 1,
                'body': None,
                'message': f'微信授权失败: {result.get("errmsg", "未知错误")}'
            })
        
        # 获取openid和session_key
        openid = result.get('openid')
        unionid = result.get('unionid')  # 如果有unionid，也保存
        session_key = result.get('session_key')
        
        if not openid:
            return jsonify({
                'error': 1,
                'body': None,
                'message': '获取用户标识失败'
            })
        
        # 查询是否已有该用户
        user = User.query.filter_by(openid=openid).first()
        
        if not user:
            # 创建新用户
            user = User(
                openid=openid,
                unionid=unionid,
                username=f'wx_{openid[-8:]}',  # 使用openid末尾8位作为用户名
                nickname=f'用户_{openid[-4:]}', # 使用openid末尾4位作为昵称
                session_key=session_key
            )
            db.session.add(user)
            db.session.commit()
        else:
            # 更新session_key和最后登录时间
            user.session_key = session_key
            user.last_login_at = datetime.now()
            db.session.commit()
        
        # 生成token
        token, expire_time = generate_token(user.id)
        
        return jsonify({
            'error': 0,
            'body': {
                'token': token,
                'userId': user.id,
                'openId': openid,
                'phoneNumber': user.phone_number,  # 如果已有手机号，一并返回
                'nickname': user.nickname,         # 返回昵称
                'avatar': user.avatar,             # 返回头像
                'expireTime': expire_time
            },
            'message': ''
        })
    
    except Exception as e:
        current_app.logger.error(f'微信登录异常: {str(e)}')
        return jsonify({
            'error': 1,
            'body': None,
            'message': '微信授权失败，请重试'
        })

@user_bp.route('/update-phone', methods=['POST'])
def update_phone():
    """更新用户手机号（通过微信加密数据获取）"""
    data = request.get_json() or {}
    
    # 获取请求参数
    encrypted_data = data.get('encryptedData')
    iv = data.get('iv')
    openid = data.get('openId')
    
    if not encrypted_data or not iv or not openid:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '参数不完整'
        })
    
    # 查询用户
    user = User.query.filter_by(openid=openid).first()
    
    if not user:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '用户不存在'
        })
    
    # 获取session_key
    session_key = user.session_key
    
    if not session_key:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '会话已过期，请重新登录'
        })
    
    try:
        # 解密手机号
        session_key_bytes = base64.b64decode(session_key)
        iv_bytes = base64.b64decode(iv)
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        
        cipher = AES.new(session_key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted = cipher.decrypt(encrypted_data_bytes)
        
        # 处理PKCS#7填充
        padding = decrypted[-1]
        if padding < 1 or padding > 32:
            padding = 0
        result = decrypted[:-padding]
        
        # 解析JSON
        result_json = json.loads(result)
        phone_number = result_json.get('phoneNumber')
        
        if not phone_number:
            return jsonify({
                'error': 1,
                'body': None,
                'message': '获取手机号失败'
            })
        
        # 检查手机号是否已绑定其他账号
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user and existing_user.id != user.id:
            # 合并账号信息
            # 这里需要根据业务需求决定如何处理账号合并
            # 简单实现：保留微信账号，删除手机号账号
            for pref in UserPreference.query.filter_by(user_id=existing_user.id).all():
                pref.user_id = user.id
            
            for record in SportRecord.query.filter_by(user_id=existing_user.id).all():
                record.user_id = user.id
                
            # 可以继续添加其他关联数据的迁移
            
            db.session.delete(existing_user)
        
        # 更新用户手机号
        user.phone_number = phone_number
        user.last_login_at = datetime.now()
        db.session.commit()
        
        return jsonify({
            'error': 0,
            'body': {
                'success': True,
                'phoneNumber': phone_number
            },
            'message': ''
        })
    
    except Exception as e:
        current_app.logger.error(f'解密手机号异常: {str(e)}')
        return jsonify({
            'error': 1,
            'body': None,
            'message': '手机号解密失败，请重试'
        })

@user_bp.route('/bind-phone', methods=['POST'])
def bind_phone():
    """手动绑定手机号（通过短信验证码）"""
    data = request.get_json() or {}
    
    # 获取请求参数
    phone = data.get('phone')
    code = data.get('code')
    openid = data.get('openId')
    
    if not phone or not code or not openid:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '参数不完整'
        })
    
    # 检查验证码是否正确
    # 这里应该有验证码校验逻辑，简化处理
    if code != '123456' and code != '111111':
        return jsonify({
            'error': 1,
            'body': None,
            'message': '验证码错误'
        })
    
    # 查询用户
    user = User.query.filter_by(openid=openid).first()
    
    if not user:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '用户不存在'
        })
    
    # 检查手机号是否已绑定其他账号
    existing_user = User.query.filter_by(phone_number=phone).first()
    if existing_user and existing_user.id != user.id:
        # 合并账号信息
        # 这里需要根据业务需求决定如何处理账号合并
        # 简单实现：保留微信账号，删除手机号账号
        for pref in UserPreference.query.filter_by(user_id=existing_user.id).all():
            pref.user_id = user.id
        
        for record in SportRecord.query.filter_by(user_id=existing_user.id).all():
            record.user_id = user.id
            
        # 可以继续添加其他关联数据的迁移
        
        db.session.delete(existing_user)
    
    # 更新用户手机号
    user.phone_number = phone
    user.last_login_at = datetime.now()
    db.session.commit()
    
    # 生成token
    token, expire_time = generate_token(user.id)
    
    return jsonify({
        'error': 0,
        'body': {
            'token': token,
            'userId': user.id,
            'expireTime': expire_time,
            'phoneNumber': phone
        },
        'message': ''
    })

@user_bp.route('/send-sms', methods=['POST'])
def send_sms():
    """发送短信验证码"""
    data = request.get_json() or {}
    
    # 获取请求参数
    phone = data.get('phone')
    
    if not phone:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '手机号不能为空'
        })
    
    # 这里应该有发送短信的逻辑，简化处理
    # 假设验证码为123456
    
    return jsonify({
        'error': 0,
        'body': {
            'success': True
        },
        'message': '验证码发送成功'
    })

@user_bp.route('/info', methods=['POST'])
@token_required
def get_user_info():
    """获取用户信息"""
    # 获取当前用户
    user = g.current_user
    
    # 转换为JSON格式
    result = user.to_dict()
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@user_bp.route('/update', methods=['POST'])
@token_required
def update_user_info():
    """更新用户信息"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 获取请求参数并更新用户信息
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'avatar' in data:
        user.avatar = data['avatar']
    if 'gender' in data:
        user.gender = data['gender']
    if 'age' in data:
        user.age = data['age']
    if 'height' in data:
        user.height = data['height']
    if 'weight' in data:
        user.weight = data['weight']
    
    # 更新运动偏好
    if 'preference' in data:
        # 删除旧的偏好
        UserPreference.query.filter_by(user_id=user.id).delete()
        
        # 添加新的偏好
        for pref in data['preference']:
            new_pref = UserPreference(user_id=user.id, preference=pref)
            db.session.add(new_pref)
    
    # 提交修改
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'success': True
        },
        'message': ''
    })

@user_bp.route('/upload-avatar', methods=['POST'])
@token_required
def upload_avatar():
    """上传头像"""
    # 获取当前用户
    user = g.current_user
    
    # 检查是否有文件上传
    if 'avatar' not in request.files:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '没有文件'
        })
    
    file = request.files['avatar']
    
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({
            'error': 1,
            'body': None,
            'message': '没有选择文件'
        })
    
    # 检查文件类型
    if not (file and allowed_file(file.filename)):
        return jsonify({
            'error': 1,
            'body': None,
            'message': '不支持的文件类型'
        })
    
    try:
        # 生成安全的文件名
        filename = secure_filename(file.filename)
        # 使用uuid生成唯一文件名
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # 获取上传文件夹路径
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        avatar_folder = os.path.join(upload_folder, 'avatars')
        
        # 确保文件夹存在
        os.makedirs(avatar_folder, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(avatar_folder, unique_filename)
        file.save(file_path)
        
        # 生成可访问的URL
        if request.host.startswith('localhost') or request.host.startswith('127.0.0.1'):
            # 本地开发环境
            avatar_url = f"{request.scheme}://{request.host}/static/uploads/avatars/{unique_filename}"
        else:
            # 生产环境，可能需要使用CDN路径
            base_url = current_app.config.get('STATIC_URL', f"{request.scheme}://{request.host}")
            avatar_url = f"{base_url}/static/uploads/avatars/{unique_filename}"
        
        # 更新用户头像
        user.avatar = avatar_url
        db.session.commit()
        
        return jsonify({
            'error': 0,
            'body': {
                'avatarUrl': avatar_url
            },
            'message': '上传成功'
        })
    
    except Exception as e:
        current_app.logger.error(f'上传头像异常: {str(e)}')
        return jsonify({
            'error': 1,
            'body': None,
            'message': '上传失败，请重试'
        })

@user_bp.route('/sport/stats', methods=['POST'])
@token_required
def get_user_sport_stats():
    """获取用户运动统计数据"""
    user = g.current_user
    
    # 查询用户的所有运动记录
    records = SportRecord.query.filter_by(user_id=user.id).all()
    
    # 计算总运动数据
    total_distance = sum(record.distance for record in records) / 1000  # 转换为公里
    total_duration = sum(record.duration for record in records) / 60  # 转换为分钟
    total_calories = sum(record.calories for record in records)
    total_sessions = len(records)
    
    # 获取当前日期
    now = datetime.now()
    
    # 计算最近一周的起始日期
    week_start = now - timedelta(days=now.weekday(), weeks=0)
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 计算最近一月的起始日期
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # 按天统计每日运动数据
    weekly_stats = []
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_end = day + timedelta(days=1)
        
        # 查询当天的运动记录
        day_records = [r for r in records if day <= r.start_time < day_end]
        
        # 计算当天的运动数据
        day_distance = sum(r.distance for r in day_records) / 1000  # 转换为公里
        day_duration = sum(r.duration for r in day_records) / 60  # 转换为分钟
        day_calories = sum(r.calories for r in day_records)
        
        weekly_stats.append({
            'date': day.strftime('%Y-%m-%d'),
            'distance': day_distance,
            'duration': day_duration,
            'calories': day_calories
        })
    
    # 按月统计每月运动数据
    monthly_stats = []
    for i in range(12):
        month = month_start.replace(month=(month_start.month - i - 1) % 12 + 1)
        if month.month == 12 and i > 0:
            month = month.replace(year=month.year - 1)
        
        next_month = month.replace(month=month.month % 12 + 1)
        if next_month.month == 1:
            next_month = next_month.replace(year=next_month.year + 1)
        
        # 查询当月的运动记录
        month_records = [r for r in records if month <= r.start_time < next_month]
        
        # 计算当月的运动数据
        month_distance = sum(r.distance for r in month_records) / 1000  # 转换为公里
        month_duration = sum(r.duration for r in month_records) / 60  # 转换为分钟
        month_calories = sum(r.calories for r in month_records)
        
        monthly_stats.append({
            'month': month.strftime('%Y-%m'),
            'distance': month_distance,
            'duration': month_duration,
            'calories': month_calories
        })
    
    return jsonify({
        'error': 0,
        'body': {
            'totalDistance': total_distance,
            'totalDuration': total_duration,
            'totalCalories': total_calories,
            'totalSessions': total_sessions,
            'weeklyStats': weekly_stats,
            'monthlyStats': monthly_stats
        },
        'message': ''
    }) 