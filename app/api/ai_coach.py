from flask import Blueprint, request, jsonify, g
from ..models import AIChatHistory, AITrainingPlan, User
from ..utils import token_required, parse_json
from .. import db
import json
import random
from datetime import datetime

ai_coach_bp = Blueprint('ai_coach', __name__)

@ai_coach_bp.route('/reply', methods=['POST'])
@token_required
def get_ai_reply():
    """获取AI教练回复"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 获取用户消息
    message = data.get('message')
    
    if not message:
        return jsonify({
            'error': 1,
            'body': None,
            'message': '消息内容不能为空'
        })
    
    # 保存用户消息
    user_msg = AIChatHistory(
        user_id=user.id,
        type='user',
        content=message
    )
    db.session.add(user_msg)
    db.session.commit()
    
    # 这里应该调用实际的AI处理逻辑，生成回复
    # 简化处理，使用预设回复
    ai_reply = generate_ai_reply(message, user)
    
    # 保存AI回复
    ai_msg = AIChatHistory(
        user_id=user.id,
        type='ai',
        content=ai_reply['reply'],
        suggestions=json.dumps(ai_reply['suggestions'])
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'id': ai_msg.id,
            'reply': ai_reply['reply'],
            'suggestions': ai_reply['suggestions'],
            'timestamp': ai_msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        },
        'message': ''
    })

@ai_coach_bp.route('/history', methods=['POST'])
@token_required
def get_chat_history():
    """获取聊天历史记录"""
    user = g.current_user
    
    # 查询该用户的所有聊天记录，按时间排序
    history = AIChatHistory.query.filter_by(user_id=user.id).order_by(AIChatHistory.created_at.asc()).all()
    
    # 转换为JSON格式
    result = [record.to_dict() for record in history]
    
    return jsonify({
        'error': 0,
        'body': result,
        'message': ''
    })

@ai_coach_bp.route('/plan', methods=['POST'])
@token_required
def get_ai_plan():
    """获取AI推荐的运动计划"""
    data = request.get_json() or {}
    user = g.current_user
    
    # 获取请求参数
    goal = data.get('goal')
    level = data.get('level')
    preference = data.get('preference', [])
    constraints = data.get('constraints', [])
    
    # 生成个性化运动计划
    # 实际应用中，这里应该调用AI模型生成计划
    # 这里使用预设的运动计划示例
    plan = generate_ai_plan(user, goal, level, preference, constraints)
    
    # 保存计划到数据库
    training_plan = AITrainingPlan(
        user_id=user.id,
        name=plan['name'],
        description=plan['description'],
        duration=plan['duration'],
        weekly_plan=json.dumps(plan['weeklyPlan'])
    )
    db.session.add(training_plan)
    db.session.commit()
    
    return jsonify({
        'error': 0,
        'body': {
            'planId': training_plan.id,
            'name': training_plan.name,
            'description': training_plan.description,
            'duration': training_plan.duration,
            'weeklyPlan': plan['weeklyPlan']
        },
        'message': ''
    })

def generate_ai_reply(message, user):
    """生成AI回复（示例实现）"""
    # 基于用户消息内容的简单回复逻辑
    reply = ""
    suggestions = []
    
    # 根据关键词匹配回复
    if '你好' in message or '您好' in message:
        reply = f"你好，{user.nickname or '用户'}！我是你的AI运动教练。今天想要了解什么运动相关的内容呢？"
        suggestions = ["如何制定运动计划？", "今天适合什么运动？", "如何提高跑步速度？"]
    elif '运动计划' in message:
        reply = "制定合适的运动计划需要考虑你的身体状况、运动目标和时间安排。我可以根据这些因素为你定制个性化的运动计划。"
        suggestions = ["我想减肥，需要什么运动计划？", "每周锻炼3次的计划建议", "如何增加肌肉？"]
    elif '减肥' in message:
        reply = "减肥需要合理的饮食控制和有氧运动相结合。建议每周进行3-5次有氧运动，每次30-60分钟，如跑步、游泳或骑自行车。"
        suggestions = ["什么食物有助于减肥？", "HIIT训练对减肥有效吗？", "如何避免运动伤害？"]
    elif '肌肉' in message or '增肌' in message:
        reply = "增肌需要进行力量训练和保证充足的蛋白质摄入。建议进行分化训练，如周一练胸和三头肌，周三练背和二头肌，周五练腿和肩。"
        suggestions = ["增肌期饮食建议", "如何正确做深蹲？", "哑铃训练计划"]
    elif '跑步' in message:
        reply = "跑步是最简单有效的有氧运动之一。建议循序渐进，开始可以采用间歇跑的方式，如跑3分钟走2分钟，逐渐增加跑步时间。"
        suggestions = ["如何提高跑步耐力？", "跑步前的热身动作", "跑步后如何恢复？"]
    else:
        reply = "作为你的AI运动教练，我可以帮你制定个性化运动计划、解答运动相关问题、提供健康建议。有什么我可以帮到你的吗？"
        suggestions = ["如何开始健身？", "推荐一些家庭健身动作", "如何保持运动动力？"]
    
    return {
        'reply': reply,
        'suggestions': suggestions
    }

def generate_ai_plan(user, goal, level, preference, constraints):
    """生成AI运动计划（示例实现）"""
    # 根据用户目标和级别生成计划
    plan_name = ""
    description = ""
    duration = 28  # 默认28天计划
    
    # 根据目标设置计划名称和描述
    if goal == '减肥':
        plan_name = "减脂塑形28天计划"
        description = "这是一个专注于减脂和塑造体形的28天计划，结合有氧运动和力量训练，帮助你健康减重并提升体能。"
    elif goal == '增肌':
        plan_name = "增肌强化训练计划"
        description = "这是一个专注于增肌和提高力量的训练计划，通过科学的分化训练和渐进式负重，帮助你有效增长肌肉。"
    elif goal == '健身':
        plan_name = "全面体能提升计划"
        description = "这是一个全面提升体能的训练计划，平衡发展力量、耐力、灵活性和心肺功能，帮助你获得全面的健康体魄。"
    else:
        plan_name = "个性化健康运动计划"
        description = "根据你的个人情况定制的运动计划，结合你的偏好和目标，帮助你建立健康的运动习惯。"
    
    # 根据级别调整计划
    level_desc = ""
    if level == '初级':
        level_desc = "初级"
        duration = 21  # 初级计划时间短一些
    elif level == '中级':
        level_desc = "中级"
    elif level == '高级':
        level_desc = "高级"
        
    if level_desc:
        plan_name = level_desc + plan_name
    
    # 生成每周计划
    weekly_plan = []
    
    # 简单示例：生成7天的计划
    for day in range(1, 8):
        activities = []
        
        # 根据星期几安排不同的训练
        if day == 1:  # 周一
            activities = generate_day_activities('上肢力量', preference, level)
        elif day == 2:  # 周二
            activities = generate_day_activities('有氧', preference, level)
        elif day == 3:  # 周三
            activities = generate_day_activities('核心', preference, level)
        elif day == 4:  # 周四
            activities = generate_day_activities('休息', preference, level)
        elif day == 5:  # 周五
            activities = generate_day_activities('下肢力量', preference, level)
        elif day == 6:  # 周六
            activities = generate_day_activities('全身', preference, level)
        else:  # 周日
            activities = generate_day_activities('拉伸恢复', preference, level)
        
        weekly_plan.append({
            'day': day,
            'activities': activities
        })
    
    return {
        'name': plan_name,
        'description': description,
        'duration': duration,
        'weeklyPlan': weekly_plan
    }

def generate_day_activities(day_type, preference, level):
    """生成每日活动（示例实现）"""
    activities = []
    
    # 根据日期类型生成活动
    if day_type == '上肢力量':
        activities.append({
            'type': '力量训练',
            'duration': 45 if level == '初级' else (60 if level == '中级' else 75),
            'intensity': '中等' if level == '初级' else ('中高' if level == '中级' else '高'),
            'description': '上肢力量训练：俯卧撑3组×12次，哑铃弯举3组×10次，三头肌下压3组×12次，肩上推3组×10次'
        })
    elif day_type == '有氧':
        activities.append({
            'type': '有氧运动',
            'duration': 30 if level == '初级' else (45 if level == '中级' else 60),
            'intensity': '中等' if level == '初级' else ('中高' if level == '中级' else '高'),
            'description': '有氧训练：快走或慢跑，保持心率在最大心率的60-70%'
        })
    elif day_type == '核心':
        activities.append({
            'type': '核心训练',
            'duration': 30 if level == '初级' else (40 if level == '中级' else 50),
            'intensity': '中等' if level == '初级' else ('中高' if level == '中级' else '高'),
            'description': '核心训练：平板支撑3组×30秒，卷腹3组×15次，侧平板支撑3组×30秒，腹斜肌转体3组×12次'
        })
    elif day_type == '下肢力量':
        activities.append({
            'type': '力量训练',
            'duration': 45 if level == '初级' else (60 if level == '中级' else 75),
            'intensity': '中等' if level == '初级' else ('中高' if level == '中级' else '高'),
            'description': '下肢力量训练：深蹲3组×12次，箭步蹲3组×10次/腿，腿举3组×12次，小腿提升3组×15次'
        })
    elif day_type == '全身':
        activities.append({
            'type': '综合训练',
            'duration': 50 if level == '初级' else (65 if level == '中级' else 80),
            'intensity': '中等' if level == '初级' else ('中高' if level == '中级' else '高'),
            'description': '全身训练：高抬腿30秒，深蹲3组×12次，俯卧撑3组×10次，划船3组×12次，卷腹3组×15次'
        })
    elif day_type == '拉伸恢复':
        activities.append({
            'type': '拉伸',
            'duration': 30,
            'intensity': '低',
            'description': '全身拉伸：每个动作保持30秒，重点拉伸大腿前后侧、胸部、背部和肩部'
        })
    elif day_type == '休息':
        activities.append({
            'type': '休息',
            'duration': 0,
            'intensity': '无',
            'description': '完全休息日，可以进行轻度活动如散步或瑜伽，促进恢复'
        })
    
    # 根据偏好调整活动
    if preference:
        # 这里可以根据用户偏好调整活动内容
        pass
    
    return activities 