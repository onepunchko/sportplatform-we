from flask import Blueprint, request, jsonify
from ..models import News, NewsCategory
import json

news_bp = Blueprint('news', __name__)

@news_bp.route('/list', methods=['POST'])
def get_news_list():
    """获取资讯列表"""
    data = request.get_json() or {}
    
    # 获取请求参数
    category = data.get('category')
    keyword = data.get('keyword')
    
    # 查询资讯列表
    query = News.query
    
    # 按分类筛选
    if category:
        query = query.filter_by(category_id=category)
        
    # 按关键词搜索
    if keyword:
        query = query.filter(News.title.like(f'%{keyword}%'))
        
    # 按时间倒序排序
    query = query.order_by(News.created_at.desc())
    
    news_list = query.all()
    
    # 转换为JSON格式
    result = [news.to_dict() for news in news_list]
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@news_bp.route('/detail', methods=['POST'])
def get_news_detail():
    """获取资讯详情"""
    data = request.get_json() or {}
    
    # 获取资讯ID
    news_id = data.get('id')
    
    if not news_id:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '资讯ID不能为空'
        })
    
    # 查询资讯详情
    news = News.query.get(news_id)
    
    if not news:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '资讯不存在'
        })
    
    # 增加浏览量
    news.views += 1
    from .. import db
    db.session.commit()
    
    # 转换为JSON格式
    result = news.to_dict(detail=True)
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@news_bp.route('/categories', methods=['POST'])
def get_news_categories():
    """获取资讯分类"""
    
    # 查询所有分类
    categories = NewsCategory.query.all()
    
    # 转换为JSON格式
    result = [category.to_dict() for category in categories]
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    }) 