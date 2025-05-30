import os
from dotenv import load_dotenv
from datetime import timedelta

# 加载.env文件中的环境变量
load_dotenv()
# 尝试加载.env.local文件
load_dotenv('.env.local', override=True)

class Config:
    """基础配置类"""
    # 密钥配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard-to-guess-string'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'hard-to-guess-jwt-key'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 微信小程序配置
    WX_APP_ID = os.environ.get('WX_APP_ID') or 'your-app-id'
    WX_APP_SECRET = os.environ.get('WX_APP_SECRET') or 'your-app-secret'
    
    # 文件上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    # 开发模式设置，用于提供模拟数据
    DEVELOPMENT_MODE = True
    
    @staticmethod
    def init_app(app):
        """初始化应用"""
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dev.db')
    DEVELOPMENT_MODE = True

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.db')
    WTF_CSRF_ENABLED = False
    DEVELOPMENT_MODE = True

class ProductionConfig(Config):
    """生产环境配置"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.db')
    DEVELOPMENT_MODE = False

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 