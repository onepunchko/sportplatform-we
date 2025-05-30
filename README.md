# 校园运动健康小程序原型

这是一个面向19-23岁大学生的运动健康类小程序的高保真原型设计。该原型使用HTML、TailwindCSS和FontAwesome构建，模拟了真实小程序的界面和交互体验。

## 项目概述

本项目针对大学生用户群体设计，满足他们对专业运动指导和参与体育活动的需求。核心功能包括：

- 智能追踪步数、卡路里，生成个性化运动报告
- 连接校园体育设施，一键预约操场、球场
- 跑步打卡、健身计划、体育课辅助，一站式满足锻炼需求
- 分享动态，结识同校运动达人
- 运动社区，分享经验，互相激励
- 运动资讯，了解最新运动趋势
- 运动挑战，参与校园运动活动
- AI运动教练，提供运动指导

## 项目结构

```
sport/
│
├── index.html             # 主入口文件，用于展示所有页面
├── components/            # 组件目录
│   ├── common.html        # 公共组件（如状态栏、底部导航）
│   └── page-template.html # 页面模板
│
├── pages/                 # 页面目录
│   ├── home.html          # 首页
│   ├── tracking.html      # 运动追踪页面
│   ├── reservation.html   # 场地预约页面
│   ├── community.html     # 运动社区页面
│   ├── profile.html       # 个人资料页面
│   ├── ai-coach.html      # AI教练页面
│   ├── challenge.html     # 运动挑战页面
│   └── news.html          # 资讯页面
│
└── assets/                # 资源目录
    ├── images/            # 图片资源
    ├── css/               # CSS样式
    └── js/                # JavaScript文件
```

## 使用说明

1. 打开`index.html`文件查看所有页面的整体布局
2. 点击每个页面上的链接或按钮可以交互，但在原型中跳转链接不会实际生效
3. 页面设计遵循iPhone 15 Pro的尺寸，模拟真实的小程序体验

## 技术栈

- HTML5
- TailwindCSS (通过CDN加载)
- FontAwesome图标库 (通过CDN加载)
- 原生JavaScript

## 设计特点

- 模拟iOS状态栏和底部导航栏，提供真实的应用体验
- 现代化UI设计，符合小程序设计规范
- 圆角化界面元素，增强视觉体验
- 使用真实UI图片替代占位符，提升原型真实感
- 响应式设计，适配不同设备查看

## 原型预览

通过浏览器打开`index.html`文件即可查看所有页面的原型预览。

## 扩展开发

本原型可直接用于实际开发：

1. 根据需要修改HTML结构
2. 添加后端API连接
3. 实现小程序前端框架（如WXML、WXSS）的转换
4. 添加更多交互功能和页面

## 注意事项

- 本原型仅作为UI/UX设计参考，不包含实际功能实现
- 图片资源使用Unsplash上的免费图片，实际开发时需替换为项目专用图片
- 部分交互效果需要JavaScript支持，原型中仅实现了基本交互

# 运动平台

基于Flask的运动平台后端，提供包括运动记录、社区互动、场地预约、AI教练等功能。

## 项目结构

```
project_root/
├── app/                   # 应用包
│   ├── __init__.py        # 初始化应用
│   ├── models.py          # 数据模型
│   ├── utils.py           # 工具函数
│   ├── api/               # API蓝图
│   │   ├── __init__.py 
│   │   ├── news.py        # 资讯模块
│   │   ├── user.py        # 用户模块
│   │   ├── sport.py       # 运动模块
│   │   ├── ai_coach.py    # AI教练模块
│   │   ├── community.py   # 社区模块
│   │   ├── venue.py       # 场地预约模块
│   ├── templates/         # 模板目录
│   ├── static/            # 静态文件
├── tests/                 # 测试目录
├── .env.example           # 环境变量示例
├── config.py              # 配置文件
├── requirements.txt       # 依赖包列表
├── run.py                 # 应用入口
```

## 功能模块

1. **资讯模块**: 提供运动相关资讯的浏览、搜索功能
2. **用户模块**: 提供用户登录、获取和更新用户信息、统计运动数据功能
3. **运动模块**: 提供运动记录、追踪、目标设置、挑战参与功能
4. **AI教练模块**: 提供智能回复、聊天历史、运动计划推荐功能
5. **社区模块**: 提供社区动态分享、点赞、评论、用户发现功能
6. **场地预约模块**: 提供场地查询、时段预约、我的预约管理功能

## 安装与运行

### 环境要求

- Python 3.7+
- MySQL 5.7+

### 安装步骤

1. 克隆代码库
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. 安装依赖包
   ```bash
   pip install -r requirements.txt
   ```

4. 配置环境变量
   ```bash
   # 复制示例环境变量文件并修改
   cp .env.example .env
   # 编辑.env文件，设置数据库连接等信息
   ```

5. 初始化数据库
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. 运行应用
   ```bash
   python run.py
   ```

应用将在 http://127.0.0.1:5000/ 启动。

## API接口

详细API接口信息请参考 [接口文档.md](接口文档.md)。

## 数据库设计

项目使用MySQL数据库，主要包含以下数据表：

- users: 用户表
- user_preferences: 用户运动偏好表
- news_categories: 资讯分类表
- news: 资讯表
- sport_records: 运动记录表
- sport_goals: 运动目标表
- sport_challenges: 运动挑战表
- challenge_participants: 挑战参与者表
- venues: 场地表
- venue_timeslots: 场地时段表
- venue_reservations: 场地预约表
- venue_reviews: 场地评价表
- community_posts: 社区帖子表
- post_comments: 帖子评论表
- post_likes: 帖子点赞表
- ai_chat_history: AI聊天历史表
- ai_training_plans: AI训练计划表

## AI教练集成

项目集成了阿里云百炼API，提供智能教练功能。

### 阿里云百炼API配置

1. 在`config/env.js`中配置以下参数：
   ```js
   // 添加阿里云百炼API配置
   AI_API_KEY: '您的API密钥',
   AI_MODEL_ENDPOINT: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions'
   ```

2. 阿里云百炼API调用注意事项：
   - 使用OpenAI兼容模式调用
   - 模型参数为`qwen3-8b`或其他阿里云支持的模型
   - 请求格式示例：
   ```js
   {
     "model": "qwen3-8b",
     "messages": [
       {"role": "system", "content": "你是一个专业的运动教练。"},
       {"role": "user", "content": "你是谁？"}
     ],
     "temperature": 0.7,
     "top_p": 0.8,
     "max_tokens": 1500
   }
   ```

3. 测试API配置
   - 可使用项目中的`test_qwen_api.py`(Python)或`test_qwen_api.js`(Node.js)测试API连接

### 模型支持的参数

阿里云百炼API支持以下参数：

- `model`: 模型名称，如`qwen3-8b`
- `messages`: 消息列表，每条消息包含`role`和`content`
- `temperature`: 温度参数，控制随机性，范围0-1
- `top_p`: 核采样参数，范围0-1
- `max_tokens`: 最大生成token数

更多参数请参考[阿里云官方文档](https://help.aliyun.com/zh/model-studio/developer-reference)。 