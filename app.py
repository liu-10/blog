from flask import Blueprint, render_template
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app
from ext import db

app = create_app()

# 创建管理器对象
manager = Manager(app=app)

# 创建迁移对象并添加命令
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


# @app.route('/')
# def index():
#     return 'ok'


if __name__ == '__main__':
    manager.run()
