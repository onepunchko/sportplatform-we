import sys
import os
import random
from datetime import datetime, timedelta
import json

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import User, AIChatHistory, AITrainingPlan

def seed_ai_data():
    """添加AI相关模拟数据"""
    print("开始添加AI相关模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 添加AI聊天历史
    chat_count = 0
    
    # 常见的用户提问
    user_questions = [
        "如何科学地进行跑步训练？",
        "健身新手应该注意什么？",
        "请推荐一些增肌的食物",
        "如何改善我的游泳姿势？",
        "每天应该喝多少水？",
        "减肥期间应该怎么安排饮食？",
        "如何避免运动损伤？",
        "如何提高我的篮球技术？",
        "有什么简单的家庭健身动作推荐？",
        "跑步时如何控制呼吸？",
        "力量训练和有氧训练应该如何搭配？"
    ]
    
    # AI回答
    ai_responses = [
        "科学的跑步训练应包括以下几点：\n\n1. 合理安排训练强度，遵循渐进原则\n2. 每周安排3-5次跑步，间隔休息\n3. 搭配不同类型的训练，如长跑、间歇跑和山坡跑\n4. 注重热身和拉伸，预防损伤\n5. 关注营养补充和充分休息\n\n初学者可以从每周跑步3次开始，每次20-30分钟，随着适应逐渐增加时间和强度。",
        "健身新手需要注意的几个关键点：\n\n1. 学习正确的动作姿势，可考虑请教练指导\n2. 从轻重量开始，循序渐进\n3. 制定合理的训练计划，不要过度训练\n4. 全面锻炼各肌群，避免肌肉不平衡\n5. 保证充足的蛋白质摄入和休息时间\n6. 坚持记录训练数据，跟踪进步\n\n开始时每周训练2-3次即可，给肌肉足够恢复时间。",
        "增肌期间推荐的食物包括：\n\n1. 优质蛋白质来源：鸡胸肉、鱼类、鸡蛋、牛奶、酸奶、豆腐\n2. 复合碳水化合物：糙米、全麦面包、燕麦、红薯\n3. 健康脂肪：坚果、橄榄油、鳄梨\n4. 蔬果类：西兰花、菠菜、香蕉、蓝莓\n\n增肌期间应保证每公斤体重1.6-2.2克的蛋白质摄入，合理安排三大营养素比例，并在训练后30分钟内补充蛋白质和碳水。",
        "改善游泳姿势的建议：\n\n1. 请专业教练进行技术分析和指导\n2. 练习基础划水和踢腿动作\n3. 使用浮板、划水板等辅助工具针对性训练\n4. 观看专业游泳运动员的视频学习正确姿势\n5. 录制自己的游泳视频进行分析\n6. 注重身体核心力量的训练\n\n最常见的自由泳技术问题包括：呼吸时身体过度转动、划水路径不合理、腿部踢水力量不足等。",
        "每天的理想饮水量因人而异，但一般建议：\n\n1. 成年人每天应饮用约2-3升水(8-12杯)\n2. 运动时每15-20分钟补充150-250ml水\n3. 运动后按体重减少量的150%补充水分\n4. 尿液颜色可作为水分充足的指标，淡黄色为宜\n\n注意：剧烈运动或高温环境下需增加饮水量，但也不宜过量饮水，以免水中毒。饮水应少量多次，均匀分布在全天。",
        "减肥期间的饮食建议：\n\n1. 控制总热量摄入，但不要过度限制(一般每天减少300-500卡)\n2. 增加蛋白质比例，帮助保持肌肉量\n3. 选择低GI碳水化合物，如全谷物和蔬菜\n4. 控制脂肪摄入，但不要完全排除健康脂肪\n5. 增加膳食纤维摄入，提高饱腹感\n6. 少食多餐，避免饥饿感导致的过量进食\n7. 避免精加工食品、糖和酒精\n\n重要的是保持可持续性，不建议极端节食，适当的热量缺口和结合运动才是健康减脂的方式。",
        "避免运动损伤的关键措施：\n\n1. 充分热身(5-10分钟的低强度有氧+动态拉伸)\n2. 正确的运动技术和姿势\n3. 合适的运动装备，特别是鞋子\n4. 循序渐进，不要突然增加运动量\n5. 注意休息和恢复，避免过度训练\n6. 运动后进行静态拉伸\n7. 注意补充水分和营养\n8. 倾听身体信号，疼痛时停止运动\n\n如已有轻微不适，建议采用RICE原则：休息(Rest)、冰敷(Ice)、加压(Compression)、抬高(Elevation)。",
        "提高篮球技术的建议：\n\n1. 基础技能训练：每天练习运球、传球和投篮\n2. 增强体能：提高爆发力、耐力和灵活性\n3. 观看比赛录像学习专业球员的技巧\n4. 参加小组对抗训练，提高实战能力\n5. 专注于提高弱项\n6. 制定针对性训练计划并坚持执行\n\n建议初学者重点练习：控球、原地投篮和基本防守姿势，打好基础再逐步提高难度。",
        "简单的家庭健身动作推荐：\n\n1. 俯卧撑：锻炼胸肌、肱三头肌和核心\n2. 深蹲：强化大腿和臀部肌群\n3. 弓步蹲：锻炼下肢和平衡能力\n4. 平板支撑：增强核心力量\n5. 仰卧起坐：锻炼腹肌\n6. 倒立俯卧撑：强化肩部肌群\n7. 哑铃划船(可用水瓶代替)：锻炼背阔肌\n8. 跳绳：全身性有氧运动\n\n建议组合这些动作，每组15-20次，3-4组，每周进行3-4次。",
        "跑步时的呼吸控制技巧：\n\n1. 采用腹式呼吸，而非胸式呼吸\n2. 尝试节奏呼吸，如2:2模式(两步吸气，两步呼气)\n3. 低强度跑步时可通过鼻子吸气，嘴巴呼气\n4. 高强度跑步时适合用嘴巴同时吸气和呼气\n5. 保持放松，不要憋气\n6. 根据路况调整呼吸节奏，上坡时可能需要更频繁的呼吸\n\n正确的呼吸可以提高跑步效率，减少岔气现象，新手需要通过练习找到最适合自己的呼吸方式。",
        "力量训练和有氧训练的合理搭配：\n\n1. 根据健身目标调整比例：增肌侧重力量，减脂侧重有氧\n2. 可采用以下几种搭配方式：\n   - 同一天先力量后有氧(适合减脂)\n   - 同一天先有氧后力量(适合提高有氧能力)\n   - 力量和有氧分开在不同日进行(减少干扰)\n   - HIIT训练结合两者优点\n3. 每周安排3-4次力量训练和2-3次有氧训练\n4. 注意不同肌群的恢复时间，避免连续训练同一肌群\n\n初学者可以尝试全身力量训练+中等强度有氧训练的组合，随着进步再细化计划。"
    ]
    
    # 建议的后续问题
    suggested_questions = [
        ["跑步需要什么装备？", "如何制定适合自己的跑步计划？", "跑步膝要如何预防？"],
        ["健身需要补充蛋白粉吗？", "新手力量训练多久一次合适？", "如何判断训练强度是否合适？"],
        ["蛋白质摄入过多会有什么影响？", "植物蛋白和动物蛋白有什么区别？", "增肌期间应该怎么安排一日三餐？"],
        ["自由泳换气技巧有哪些？", "如何提高游泳的耐力？", "游泳后如何保护皮肤和头发？"],
        ["喝水过多会有什么副作用？", "运动饮料和白水哪个更好？", "晨起一杯水有什么好处？"],
        ["间歇性断食对减肥有效吗？", "减肥平台期怎么突破？", "有哪些容易让人摄入过量热量的食物？"],
        ["运动后肌肉酸痛怎么缓解？", "慢性运动损伤如何判断？", "什么是正确的热身方法？"],
        ["如何提高投篮命中率？", "篮球力量训练有哪些？", "如何提高篮球比赛中的意识？"],
        ["没有器械如何锻炼背部？", "家庭健身多久能看到效果？", "有氧运动和力量训练哪个先做？"],
        ["长跑呼吸和短跑呼吸有什么不同？", "如何避免跑步时岔气？", "呼吸频率应该跟着步频调整吗？"],
        ["力量训练后多久可以进行有氧运动？", "有氧和力量如何结合更有利于减脂？", "HIIT训练的优势是什么？"]
    ]
    
    # 为部分用户创建聊天历史
    for user in users[:3]:  # 只为前3个用户创建聊天记录
        # 每个用户创建2-5组对话
        num_conversations = random.randint(2, 5)
        
        for i in range(num_conversations):
            # 随机选择一个问题和回答对
            qa_index = random.randint(0, len(user_questions) - 1)
            question = user_questions[qa_index]
            answer = ai_responses[qa_index]
            suggestions = suggested_questions[qa_index]
            
            # 创建时间（最近7天内）
            chat_time = datetime.now() - timedelta(days=random.randint(0, 7), 
                                                  hours=random.randint(0, 23),
                                                  minutes=random.randint(0, 59))
            
            # 用户提问
            user_message = AIChatHistory(
                user_id=user.id,
                type='user',
                content=question,
                created_at=chat_time
            )
            
            db.session.add(user_message)
            chat_count += 1
            
            # AI回答（时间略晚于提问）
            ai_message = AIChatHistory(
                user_id=user.id,
                type='ai',
                content=answer,
                suggestions=json.dumps(suggestions),
                created_at=chat_time + timedelta(seconds=random.randint(1, 5))
            )
            
            db.session.add(ai_message)
            chat_count += 1
            
            # 随机决定是否有后续对话
            if random.random() > 0.6:  # 40%概率有后续对话
                # 用户选择了一个建议的问题继续提问
                follow_up_question = random.choice(suggestions)
                follow_up_time = chat_time + timedelta(minutes=random.randint(1, 3))
                
                follow_up_message = AIChatHistory(
                    user_id=user.id,
                    type='user',
                    content=follow_up_question,
                    created_at=follow_up_time
                )
                
                db.session.add(follow_up_message)
                chat_count += 1
                
                # AI回答跟进问题
                follow_up_answer = "这是对您问题的详细回答，包含专业建议和实用信息。"
                if follow_up_question.find("装备") >= 0:
                    follow_up_answer = "跑步装备的选择非常重要，良好的装备可以提升体验并预防伤害。核心装备包括：\n\n1. 跑鞋：最关键的装备，应根据脚型、跑步方式和场地选择，建议专业跑鞋店测试后购买\n2. 速干运动服：吸汗透气，避免棉质衣物\n3. 运动袜：缓震防滑，避免起泡\n4. 运动手表/手机APP：记录跑步数据\n5. 补给品：长距离跑步需备水和能量胶\n\n根据季节和环境可能还需要：防晒霜、帽子、反光装备(夜跑)、压缩衣裤(寒冷天气)等。装备投资应循序渐进，先确保基础装备舒适合适。"
                elif follow_up_question.find("蛋白粉") >= 0:
                    follow_up_answer = "关于健身是否需要补充蛋白粉，没有绝对的答案，这取决于个人情况：\n\n不必须补充的情况：\n1. 通过日常饮食已能摄入足够蛋白质(每公斤体重1.6-2.2g)\n2. 训练强度较低或刚开始健身\n3. 主要目标是保持健康而非增肌\n\n可考虑补充的情况：\n1. 饮食中难以摄入足够蛋白质(如素食者)\n2. 高强度训练或增肌期\n3. 日程紧张，需要便捷的蛋白质来源\n\n蛋白粉仅是食品补充剂，不是必需品。如选择使用，优先考虑成分简单、添加剂少的产品，并遵循产品建议用量。最重要的是均衡饮食和合理训练。"
                
                ai_follow_up = AIChatHistory(
                    user_id=user.id,
                    type='ai',
                    content=follow_up_answer,
                    created_at=follow_up_time + timedelta(seconds=random.randint(1, 5))
                )
                
                db.session.add(ai_follow_up)
                chat_count += 1
    
    db.session.commit()
    
    # 创建AI训练计划
    training_plans = [
        {
            'name': '跑步入门训练计划',
            'description': '为跑步初学者设计的6周训练计划，从零基础开始，逐步提高跑步能力。',
            'duration': 42,  # 6周
            'weekly_plan': [
                {
                    'week': 1,
                    'focus': '建立基础',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 20, 'distance': 2},
                        {'day': 3, 'activity': '步行+慢跑间歇', 'duration': 25, 'distance': 2.5},
                        {'day': 5, 'activity': '轻松慢跑', 'duration': 20, 'distance': 2}
                    ]
                },
                {
                    'week': 2,
                    'focus': '增加距离',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 25, 'distance': 2.5},
                        {'day': 3, 'activity': '步行+慢跑间歇', 'duration': 30, 'distance': 3},
                        {'day': 5, 'activity': '轻松慢跑', 'duration': 25, 'distance': 2.5}
                    ]
                },
                {
                    'week': 3,
                    'focus': '提高持续性',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 30, 'distance': 3},
                        {'day': 3, 'activity': '速度变化跑', 'duration': 30, 'distance': 3},
                        {'day': 5, 'activity': '轻松慢跑', 'duration': 35, 'distance': 3.5}
                    ]
                },
                {
                    'week': 4,
                    'focus': '适应连续跑',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 30, 'distance': 3},
                        {'day': 3, 'activity': '速度变化跑', 'duration': 35, 'distance': 3.5},
                        {'day': 5, 'activity': '中等距离跑', 'duration': 40, 'distance': 4}
                    ]
                },
                {
                    'week': 5,
                    'focus': '增加强度',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 35, 'distance': 3.5},
                        {'day': 3, 'activity': '间歇训练', 'duration': 35, 'distance': 4},
                        {'day': 5, 'activity': '长距离慢跑', 'duration': 45, 'distance': 4.5}
                    ]
                },
                {
                    'week': 6,
                    'focus': '巩固成果',
                    'sessions': [
                        {'day': 1, 'activity': '轻松慢跑', 'duration': 40, 'distance': 4},
                        {'day': 3, 'activity': '速度变化跑', 'duration': 40, 'distance': 4.5},
                        {'day': 5, 'activity': '5公里挑战', 'duration': 50, 'distance': 5}
                    ]
                }
            ]
        },
        {
            'name': '30天全身塑形计划',
            'description': '通过30天的全身训练，改善体态，增强肌肉力量，提高身体代谢率。',
            'duration': 30,
            'weekly_plan': [
                {
                    'week': 1,
                    'focus': '适应训练',
                    'sessions': [
                        {'day': 1, 'activity': '上肢训练', 'exercises': ['俯卧撑10x3', '哑铃肩推8x3', '哑铃划船10x3']},
                        {'day': 2, 'activity': '核心训练', 'exercises': ['平板支撑30秒x3', '卷腹15x3', '俄罗斯转体10x3']},
                        {'day': 3, 'activity': '下肢训练', 'exercises': ['深蹲12x3', '弓步蹲10x3', '小腿提踵15x3']},
                        {'day': 5, 'activity': '全身训练', 'exercises': ['Burpees8x3', '俯卧撑8x3', '深蹲10x3', '平板支撑30秒x3']}
                    ]
                },
                {
                    'week': 2,
                    'focus': '增加强度',
                    'sessions': [
                        {'day': 1, 'activity': '上肢训练', 'exercises': ['俯卧撑12x3', '哑铃肩推10x3', '哑铃划船12x3', '三头肌屈伸12x3']},
                        {'day': 2, 'activity': '核心训练', 'exercises': ['平板支撑45秒x3', '卷腹20x3', '俄罗斯转体15x3', '山峰式30秒x3']},
                        {'day': 3, 'activity': '下肢训练', 'exercises': ['深蹲15x3', '弓步蹲12x3', '小腿提踵20x3', '箭步蹲10x3']},
                        {'day': 5, 'activity': '全身训练', 'exercises': ['Burpees10x3', '俯卧撑10x3', '深蹲12x3', '平板支撑45秒x3']}
                    ]
                },
                {
                    'week': 3,
                    'focus': '提高挑战',
                    'sessions': [
                        {'day': 1, 'activity': '上肢+核心', 'exercises': ['俯卧撑15x3', '哑铃肩推12x3', '平板支撑60秒x3', '卷腹25x3']},
                        {'day': 2, 'activity': '下肢+核心', 'exercises': ['深蹲18x3', '弓步蹲15x3', '俄罗斯转体20x3', '山峰式45秒x3']},
                        {'day': 3, 'activity': '有氧+力量', 'exercises': ['高抬腿30秒x3', '跳跃深蹲12x3', '俯卧撑12x3', '侧平板30秒x3']},
                        {'day': 5, 'activity': '全身训练', 'exercises': ['Burpees12x4', '俯卧撑12x4', '深蹲15x4', '平板支撑60秒x3']}
                    ]
                },
                {
                    'week': 4,
                    'focus': '巅峰挑战',
                    'sessions': [
                        {'day': 1, 'activity': '上肢+核心', 'exercises': ['俯卧撑变式15x3', '哑铃肩推15x3', '动态平板60秒x3', '腹肌转体30x3']},
                        {'day': 2, 'activity': '下肢+核心', 'exercises': ['深蹲跳12x3', '弓步蹲带跳15x3', 'V字卷腹15x3', '侧平板提升30秒x3']},
                        {'day': 3, 'activity': 'HIIT训练', 'exercises': ['30秒工作/15秒休息x8组', '包含：高抬腿、深蹲跳、俯卧撑、登山跑']},
                        {'day': 5, 'activity': '全身挑战', 'exercises': ['复合动作循环20分钟', '包含所有前期训练的核心动作']},
                        {'day': 7, 'activity': '最终测试', 'exercises': ['1分钟俯卧撑', '1分钟深蹲', '最长平板支撑', '对比第一天记录']}
                    ]
                }
            ]
        }
    ]
    
    plan_count = 0
    
    for user in users[:3]:  # 只为前3个用户创建训练计划
        # 为每个用户创建1-2个训练计划
        num_plans = random.randint(1, 2)
        
        for i in range(num_plans):
            # 随机选择一个计划模板
            plan_template = random.choice(training_plans)
            
            # 创建时间（最近30天内）
            created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            plan = AITrainingPlan(
                user_id=user.id,
                name=plan_template['name'],
                description=plan_template['description'],
                duration=plan_template['duration'],
                weekly_plan=json.dumps(plan_template['weekly_plan']),
                created_at=created_at
            )
            
            db.session.add(plan)
            plan_count += 1
    
    db.session.commit()
    print(f"成功创建了 {chat_count} 条AI聊天记录和 {plan_count} 个AI训练计划")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_ai_data() 