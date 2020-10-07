
from flask import Flask
from flask import Blueprint
# from sqlalchemy.testing.plugin import bootstrap

import setting
from app.goods.views import article_app
from app.user.views import user_app
from ext import db


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # 加载配置
    app.config.from_object(setting.Config)

    # 初始化app
    db.init_app(app)
    # bootstrap.init_app(app)

    # 注册蓝图
    app.register_blueprint(user_app)
    app.register_blueprint(article_app)

    return app

