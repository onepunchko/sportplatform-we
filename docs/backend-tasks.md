# 后端API开发任务清单

## 1. 新增评论动态API

- **路径**: `/community/post/comment`
- **方法**: POST
- **请求参数**:
  ```json
  {
    "postId": 1,
    "content": "这是评论内容"
  }
  ```
- **返回结构**:
  ```json
  {
    "error": 0,
    "body": {
      "id": 123,
      "content": "这是评论内容",
      "user": {
        "id": 1,
        "name": "用户名",
        "avatar": "头像URL"
      },
      "createTime": "2023-05-15 10:30:00"
    },
    "message": "评论成功"
  }
  ```
- **功能**: 用户对社区动态进行评论
- **优先级**: High
- **关联模块**: 社区评论功能

## 2. 查询动态评论列表API

- **路径**: `/community/post/comments`
- **方法**: GET
- **请求参数**:
  ```json
  {
    "postId": 1,
    "page": 1,
    "pageSize": 10
  }
  ```
- **返回结构**:
  ```json
  {
    "error": 0,
    "body": {
      "total": 25,
      "list": [
        {
          "id": 123,
          "content": "评论内容1",
          "user": {
            "id": 1,
            "name": "用户A",
            "avatar": "头像URL"
          },
          "createTime": "2023-05-15 10:30:00"
        },
        {
          "id": 124,
          "content": "评论内容2",
          "user": {
            "id": 2,
            "name": "用户B",
            "avatar": "头像URL"
          },
          "createTime": "2023-05-15 11:20:00"
        }
      ]
    },
    "message": "获取成功"
  }
  ```
- **功能**: 获取某条动态的评论列表
- **优先级**: High
- **关联模块**: 社区评论展示功能

## 3. 后端实现方案

### 数据库设计

需要创建评论表：

```sql
CREATE TABLE comment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL COMMENT '动态ID',
    user_id INT NOT NULL COMMENT '评论用户ID',
    content TEXT NOT NULL COMMENT '评论内容',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '状态：1-正常，0-删除',
    INDEX idx_post_id (post_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='动态评论表';
```

### Python Flask实现示例

```python
from flask import Blueprint, request, jsonify, g
from ..models import Post, Comment, User
from ..utils import token_required
from .. import db
from datetime import datetime

# 创建蓝图
comment_bp = Blueprint('comment', __name__)

@comment_bp.route('/community/post/comment', methods=['POST'])
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
    
    post_id = data.get('postId')
    content = data.get('content')
    
    if not post_id or not content:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '参数不完整'
        })
    
    # 验证动态是否存在
    post = Post.query.get(post_id)
    if not post:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '动态不存在'
        })
    
    # 创建评论
    comment = Comment(
        post_id=post_id,
        user_id=g.user.id,
        content=content
    )
    
    db.session.add(comment)
    db.session.commit()
    
    # 更新动态评论数
    post.comments_count = Post.comments_count + 1
    db.session.commit()
    
    # 返回评论信息
    return jsonify({
        'error': 0,
        'body': {
            'id': comment.id,
            'content': comment.content,
            'user': {
                'id': g.user.id,
                'name': g.user.nickname,
                'avatar': g.user.avatar
            },
            'createTime': comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'message': '评论成功'
    })

@comment_bp.route('/community/post/comments', methods=['GET'])
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
    
    # 查询评论总数
    total = Comment.query.filter_by(post_id=post_id, status=1).count()
    
    # 分页查询评论
    comments = Comment.query.filter_by(post_id=post_id, status=1) \
        .order_by(Comment.create_time.desc()) \
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
                'createTime': comment.create_time.strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return jsonify({
        'error': 0,
        'body': {
            'total': total,
            'list': comment_list
        },
        'message': '获取成功'
    })
```

### 注册路由

在`__init__.py`或主应用文件中注册上述蓝图：

```python
from .api.comment import comment_bp

def create_app(config_name):
    # ...其他代码
    
    # 注册蓝图
    app.register_blueprint(comment_bp, url_prefix='/api')
    
    # ...其他代码
    return app 