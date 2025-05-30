import sys
import os
import random
from datetime import datetime, timedelta, date
import json

# 将项目根目录添加到 Python 路径中
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Venue, VenueTimeSlot, VenueReservation, VenueReview, User

def seed_venues():
    """添加场馆相关模拟数据"""
    print("开始添加场馆相关模拟数据...")
    
    # 获取所有用户
    users = User.query.all()
    if not users:
        print("数据库中没有用户数据，请先运行 seed_users.py")
        return
    
    # 创建场馆数据
    venues_data = [
        {
            'name': '大学体育馆',
            'type': 'sports_center',
            'location': '北京市海淀区颐和园路5号',
            'description': '大学主体育馆，设施齐全，环境优美。提供篮球、排球、羽毛球、乒乓球等多种运动场地。',
            'images': ['/static/images/venues/venue1_1.jpg', '/static/images/venues/venue1_2.jpg'],
            'capacity': 500,
            'open_time': '08:00',
            'close_time': '22:00',
            'price': 50.0,
            'facilities': ['空调', '淋浴', '更衣室', '饮水机', '停车场'],
            'rules': ['禁止吸烟', '禁止饮食', '穿运动鞋入场']
        },
        {
            'name': '阳光游泳馆',
            'type': 'swimming',
            'location': '北京市朝阳区建国路88号',
            'description': '室内恒温游泳馆，水质清澈，环境舒适。提供标准泳道和儿童戏水区。',
            'images': ['/static/images/venues/venue2_1.jpg', '/static/images/venues/venue2_2.jpg'],
            'capacity': 200,
            'open_time': '06:00',
            'close_time': '22:00',
            'price': 80.0,
            'facilities': ['更衣室', '淋浴', '吹风机', '泳具出租', '教练服务'],
            'rules': ['必须戴泳帽', '冲洗后入池', '禁止跳水']
        },
        {
            'name': '星光篮球场',
            'type': 'basketball',
            'location': '北京市西城区德胜门外大街16号',
            'description': '室外篮球场，设有标准篮球场4个，场地宽敞，灯光充足，适合夜间比赛。',
            'images': ['/static/images/venues/venue3_1.jpg'],
            'capacity': 100,
            'open_time': '09:00',
            'close_time': '23:00',
            'price': 30.0,
            'facilities': ['饮水机', '休息区', '篮球出租'],
            'rules': ['禁止吸烟', '爱护场地设施']
        },
        {
            'name': '康体健身中心',
            'type': 'fitness',
            'location': '北京市朝阳区东三环中路39号',
            'description': '现代化健身中心，配备先进健身器材，提供私教服务，环境舒适。',
            'images': ['/static/images/venues/venue4_1.jpg', '/static/images/venues/venue4_2.jpg'],
            'capacity': 150,
            'open_time': '07:00',
            'close_time': '23:00',
            'price': 100.0,
            'facilities': ['淋浴', '更衣室', '有氧区', '力量区', '拉伸区', '按摩服务'],
            'rules': ['自备毛巾', '器械使用后归位', '禁止光脚锻炼']
        },
        {
            'name': '羽毛球馆',
            'type': 'badminton',
            'location': '北京市海淀区中关村南大街5号',
            'description': '专业羽毛球场馆，设有8片标准场地，地板采用专业PVC材质，场地隔音效果好。',
            'images': ['/static/images/venues/venue5_1.jpg'],
            'capacity': 80,
            'open_time': '10:00',
            'close_time': '22:00',
            'price': 60.0,
            'facilities': ['更衣室', '饮水机', '球拍租赁', '羽毛球售卖'],
            'rules': ['穿运动鞋入场', '禁止饮食']
        }
    ]
    
    venue_ids = []
    
    for venue_data in venues_data:
        # 检查场馆是否已存在
        existing_venue = Venue.query.filter_by(name=venue_data['name']).first()
        if existing_venue:
            venue_ids.append(existing_venue.id)
            print(f"场馆 {venue_data['name']} 已存在，跳过创建")
            continue
        
        # 准备JSON字段
        images_json = json.dumps(venue_data['images'])
        facilities_json = json.dumps(venue_data['facilities'])
        rules_json = json.dumps(venue_data['rules'])
        
        venue = Venue(
            name=venue_data['name'],
            type=venue_data['type'],
            location=venue_data['location'],
            description=venue_data['description'],
            images=images_json,
            capacity=venue_data['capacity'],
            open_time=venue_data['open_time'],
            close_time=venue_data['close_time'],
            price=venue_data['price'],
            facilities=facilities_json,
            rules=rules_json,
            created_at=datetime.now() - timedelta(days=random.randint(30, 90))
        )
        
        db.session.add(venue)
        db.session.flush()  # 获取ID
        venue_ids.append(venue.id)
    
    # 提交以获取场馆ID
    db.session.commit()
    
    # 为每个场馆创建时段
    time_slots_data = [
        {'start': '08:00', 'end': '10:00'},
        {'start': '10:00', 'end': '12:00'},
        {'start': '14:00', 'end': '16:00'},
        {'start': '16:00', 'end': '18:00'},
        {'start': '18:00', 'end': '20:00'},
        {'start': '20:00', 'end': '22:00'}
    ]
    
    for venue_id in venue_ids:
        venue = Venue.query.get(venue_id)
        base_price = venue.price
        
        for slot_data in time_slots_data:
            # 跳过不在营业时间内的时段
            if slot_data['start'] < venue.open_time or slot_data['end'] > venue.close_time:
                continue
                
            # 检查时段是否已存在
            existing_slot = VenueTimeSlot.query.filter_by(
                venue_id=venue_id,
                start_time=slot_data['start'],
                end_time=slot_data['end']
            ).first()
            
            if existing_slot:
                continue
            
            # 晚间时段价格略高
            price_factor = 1.2 if slot_data['start'] >= '18:00' else 1.0
            # 周末价格略高
            weekend_factor = 1.3
            
            slot = VenueTimeSlot(
                venue_id=venue_id,
                start_time=slot_data['start'],
                end_time=slot_data['end'],
                price=round(base_price * price_factor, 2),
                created_at=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            
            db.session.add(slot)
    
    db.session.commit()
    print(f"成功创建了 {len(venue_ids)} 个场馆及其时段")
    
    # 创建一些预约记录
    reservation_count = 0
    all_slots = VenueTimeSlot.query.all()
    
    for user in users:
        # 每个用户创建0-3条预约记录
        num_reservations = random.randint(0, 3)
        
        for i in range(num_reservations):
            # 随机选择一个时段
            slot = random.choice(all_slots)
            
            # 选择一个日期（未来7天内）
            reservation_date = date.today() + timedelta(days=random.randint(1, 7))
            
            # 创建预约
            status_choices = ['pending', 'confirmed', 'completed', 'cancelled']
            status_weights = [0.3, 0.3, 0.3, 0.1]  # 加权概率
            status = random.choices(status_choices, weights=status_weights, k=1)[0]
            
            cancelled_at = None
            if status == 'cancelled':
                cancelled_at = datetime.now() - timedelta(hours=random.randint(1, 48))
            
            # 参与人数
            participants = random.randint(1, 5)
            
            # 价格（基于时段价格和人数）
            price = slot.price * participants
            
            reservation = VenueReservation(
                user_id=user.id,
                venue_id=slot.venue_id,
                timeslot_id=slot.id,
                date=reservation_date,
                participants=participants,
                remark="无特殊要求" if random.random() > 0.3 else "请准备好饮用水",
                status=status,
                price=price,
                created_at=datetime.now() - timedelta(days=random.randint(1, 7)),
                cancelled_at=cancelled_at
            )
            
            db.session.add(reservation)
            reservation_count += 1
    
    db.session.commit()
    print(f"成功创建了 {reservation_count} 条场馆预约记录")
    
    # 添加一些场馆评价
    review_count = 0
    
    for venue_id in venue_ids:
        # 每个场馆添加3-8条评价
        num_reviews = random.randint(3, 8)
        
        for i in range(num_reviews):
            # 随机选择一个用户
            user = random.choice(users)
            
            # 评分（倾向于好评）
            rating_weights = [0.05, 0.1, 0.15, 0.3, 0.4]  # 1-5星的权重
            rating = random.choices([1, 2, 3, 4, 5], weights=rating_weights, k=1)[0]
            
            # 评价内容
            comments = [
                "场地很干净，服务态度好。",
                "设施比较完善，就是人有点多。",
                "交通便利，价格合理，会再来的。",
                "教练很专业，学到了很多。",
                "空间宽敞，通风良好，很舒适。",
                "停车方便，场地维护得不错。",
                "设备有点旧了，但总体还可以。",
                "服务人员态度亲切，环境不错。",
                "性价比高，推荐给朋友们。",
                "离家近，很方便，经常来。"
            ]
            
            # 根据评分调整评价内容
            if rating <= 2:
                comments = [
                    "设施有点旧，需要更新了。",
                    "服务态度一般，有待提高。",
                    "价格偏贵，不太值得。",
                    "环境比较嘈杂，不太满意。",
                    "卫生条件有待改善。"
                ]
            
            comment = random.choice(comments)
            
            # 检查是否已存在评价
            existing_review = VenueReview.query.filter_by(
                user_id=user.id,
                venue_id=venue_id
            ).first()
            
            if existing_review:
                continue
            
            review = VenueReview(
                user_id=user.id,
                venue_id=venue_id,
                rating=rating,
                comment=comment,
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            
            db.session.add(review)
            review_count += 1
    
    db.session.commit()
    print(f"成功创建了 {review_count} 条场馆评价")

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        seed_venues() 