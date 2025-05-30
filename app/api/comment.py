from flask import Blueprint, request, jsonify, g, current_app
from ..models import User, CommunityPost, PostComment
from ..utils import token_required
from .. import db
from datetime import datetime

# 创建蓝图
comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/post/comment', methods=['POST'])
@token_required
def comment_post():
    """评论动态"""
    data = request.get_json()
    if not data:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '请求参数错误'
        })
    
    # 检查用户认证
    if not hasattr(g, 'current_user') or g.current_user is None:
        return jsonify({
            'error': 401,
            'body': None,
            'message': '用户未登录或认证失败'
        })
    
    post_id = data.get('postId')
    content = data.get('content')
    
    if not post_id or not content:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '参数不完整'
        })
    
    # 验证动态是否存在
    post = CommunityPost.query.get(post_id)
    if not post:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '动态不存在'
        })
    
    try:
        # 创建评论
        comment = PostComment(
            post_id=post_id,
            user_id=g.current_user.id,
            content=content,
            created_at=datetime.now()
        )
        
        db.session.add(comment)
        db.session.commit()
        
        # 获取用户信息
        user = User.query.get(g.current_user.id)
        
        if not user:
            # 如果找不到用户信息，使用基本信息
            return jsonify({
                'error': 0,
                'body': {
                    'id': comment.id,
                    'content': comment.content,
                    'user': {
                        'id': g.current_user.id,
                        'name': f'用户{g.current_user.id}',
                        'avatar': '/static/images/default_avatar.png'
                    },
                    'createTime': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                },
                'message': '评论成功'
            })
        
        # 返回评论信息
        return jsonify({
            'error': 0,
            'body': {
                'id': comment.id,
                'content': comment.content,
                'user': {
                    'id': user.id,
                    'name': user.nickname,
                    'avatar': user.avatar
                },
                'createTime': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            },
            'message': '评论成功'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'添加评论异常: {str(e)}')
        return jsonify({
            'error': 1,
            'body': None,
            'message': f'评论失败: {str(e)}'
        })

@comment_bp.route('/post/comments', methods=['GET'])
def get_post_comments():
    """获取动态评论列表"""
    post_id = request.args.get('postId', type=int)
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    
    if not post_id:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '参数不完整'
        })
    
    try:
        # 查询评论总数
        total = PostComment.query.filter_by(post_id=post_id).count()
        
        # 分页查询评论
        comments = PostComment.query.filter_by(post_id=post_id) \
            .order_by(PostComment.created_at.desc()) \
            .offset((page - 1) * page_size) \
            .limit(page_size) \
            .all()
        
        # 构建返回数据
        comment_list = []
        for comment in comments:
            user = User.query.get(comment.user_id)
            if user:
                comment_list.append({
                    'id': comment.id,
                    'content': comment.content,
                    'user': {
                        'id': user.id,
                        'name': user.nickname,
                        'avatar': user.avatar
                    },
                    'createTime': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return jsonify({
            'error': 0,
            'body': {
                'total': total,
                'list': comment_list
            },
            'message': '获取成功'
        })
    except Exception as e:
        current_app.logger.error(f'获取评论列表异常: {str(e)}')
        return jsonify({
            'error': 1,
            'body': None,
            'message': f'获取评论列表失败: {str(e)}'
        }) 