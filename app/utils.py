from flask import request, jsonify, g, current_app
from functools import wraps
import jwt
from datetime import datetime, timedelta
import time
from .models import User

def generate_token(user_id):
    """生成JWT token"""
    # 获取密钥
    secret_key = current_app.config['JWT_SECRET_KEY']
    
    # 设置token过期时间为7天
    expire_time = int(time.time()) + 7 * 24 * 60 * 60
    
    # 生成token
    payload = {
        'user_id': user_id,
        'exp': expire_time
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    
    # 如果token为bytes，转换为str
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    return token, expire_time

def token_required(f):
    """验证token的装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 获取token（支持多种请求头格式）
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        # 如果没有找到Authorization头，尝试从auth头获取
        if not token:
            token = request.headers.get('auth')
        
        if not token:
            # 检查是否开启了开发模式模拟数据
            if current_app.config.get('DEVELOPMENT_MODE', False):
                # 创建模拟用户
                mock_user = User()
                mock_user.id = 999
                mock_user.username = 'mock_user'
                mock_user.nickname = '模拟用户'
                mock_user.avatar = '/static/images/default_avatar.png'
                g.current_user = mock_user
                return f(*args, **kwargs)
            
            return jsonify({
                'error': 2,
                'body': None,
                'message': '缺少token，请先登录'
            }), 401
        
        try:
            # 验证token
            secret_key = current_app.config['JWT_SECRET_KEY']
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 获取用户ID
            user_id = payload['user_id']
            
            # 查询用户
            current_user = User.query.get(user_id)
            
            if not current_user:
                # 如果用户不存在但开启了开发模式，使用模拟用户
                if current_app.config.get('DEVELOPMENT_MODE', False):
                    # 创建模拟用户
                    mock_user = User()
                    mock_user.id = 999
                    mock_user.username = 'mock_user'
                    mock_user.nickname = '模拟用户'
                    mock_user.avatar = 'default-avatar.png'
                    g.current_user = mock_user
                    return f(*args, **kwargs)
                
                return jsonify({
                    'error': 2,
                    'body': None,
                    'message': '无效的token，用户不存在'
                }), 401
            
            # 将当前用户保存到g对象中
            g.current_user = current_user
            
        except jwt.ExpiredSignatureError:
            # 如果token过期但开启了开发模式，使用模拟用户
            if current_app.config.get('DEVELOPMENT_MODE', False):
                # 创建模拟用户
                mock_user = User()
                mock_user.id = 999
                mock_user.username = 'mock_user'
                mock_user.nickname = '模拟用户'
                mock_user.avatar = 'default-avatar.png'
                g.current_user = mock_user
                return f(*args, **kwargs)
            
            return jsonify({
                'error': 2,
                'body': None,
                'message': 'token已过期，请重新登录'
            }), 401
        except jwt.InvalidTokenError:
            # 如果token无效但开启了开发模式，使用模拟用户
            if current_app.config.get('DEVELOPMENT_MODE', False):
                # 创建模拟用户
                mock_user = User()
                mock_user.id = 999
                mock_user.username = 'mock_user'
                mock_user.nickname = '模拟用户'
                mock_user.avatar = 'default-avatar.png'
                g.current_user = mock_user
                return f(*args, **kwargs)
            
            return jsonify({
                'error': 2,
                'body': None,
                'message': '无效的token'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated

def parse_json(json_str):
    """解析JSON字符串，失败时返回空列表或字典"""
    import json
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except:
        return [] 