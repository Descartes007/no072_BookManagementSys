from flask_jwt_extended import JWTManager
from flask_redis import FlaskRedis
import settings
from apps.classification.views import book_type_bp
from exts import db
from flask_cors import *
from flask import Flask, request
from flask_login import LoginManager
from flask_session import Session
from apps.User.views import user_bp
from apps.publish.views import publisher_bp
from apps.author.views import author_bp
from apps.book.views import book_bp
from apps.notice.views import notice_bp
from apps.role.views import role_bp
from apps.audit.views import audit_bp
from apps.views import global_bp
from exts.logHandler import base_logger as logger


def create_app(config_name):
    app = Flask(__name__, static_folder=settings.Config.UPLOAD_FOLDER)
    if config_name == 'production':
        app.config.from_object(settings.ProductionConfig)
        # 设置允许跨域，是否允许请求发送cookie，False是不允许，True是允许
        CORS(app, supports_credentials=True, origins=[settings.ProductionConfig.VUE_ADDR])
    else:
        app.config.from_object(settings.DevelopmentConfig)
        # 设置允许跨域，是否允许请求发送cookie，False是不允许，True是允许
        CORS(app, supports_credentials=True, origins=[settings.DevelopmentConfig.VUE_ADDR])

    # 初始化数据库
    db.init_app(app)
    redis_store = FlaskRedis(app)
    # 初始化 JWTManager
    jwt = JWTManager(app)
    # Session(app)
    # # 创建登录管理器实例
    # login_manager = LoginManager()
    # # 初始化登录管理器
    # login_manager.init_app(app)
    # login_manager.login_view = 'user.user_login'  # user蓝图的user_login视图函数

    # 注册蓝图
    app.register_blueprint(user_bp)
    app.register_blueprint(publisher_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(book_type_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(notice_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(global_bp)

    # # 定义用户加载回调函数
    # @login_manager.user_loader
    # def load_user(user_id):
    #     # 通过延迟导入避免循环导入
    #     from apps.User.model import User
    #     return User.query.get(int(user_id))

    # 请求到达flask，但是还没有进入到具体的视图函数之前调用，一般用于在调用视图函数之前，准备或处理一些后面可能会用到的数据，
    @app.before_request
    def print_request_info():
        logger.debug("接口请求地址:" + request.url)
        # 文件上传接口不需要打印请求内容
        if request.endpoint == 'book.file_upload' or request.endpoint == 'book.excel_upload':
            pass
        else:
            logger.debug("接口请求数据:" + request.get_data().decode('utf-8'))

    # 处理请求后无异常执行该钩子函数
    # @app.after_request
    # def print_request_data(response):
    #     logger.debug("接口请求返回11111:" + response.get_data().decode('utf-8'))
    #     return response
    return app
