import random
from datetime import datetime

from ext import db


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(16), nullable=True)
    password = db.Column(db.String(256), nullable=True)
    phone = db.Column(db.String(11), unique=True)
    email = db.Column(db.String(20), unique=True)
    join_time = db.Column(db.DateTime, default=datetime.now)
    icon = db.Column(db.String(128))
    abe = db.Column(db.String(128), nullable=True)
    article = db.relationship('Article', backref='users')
    photo = db.relationship('Photo', backref='user_photo')
    comment = db.relationship('Vcomment', backref='user_comment')
    collect = db.relationship('Collect', backref='user_collect')
    message = db.relationship('Message', backref='user_message')

    def __str__(self):
        return self.name


class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_name = db.Column(db.String(16), unique=True)
    # numbers = db.Column(db.Integer, default=''.join(random.choices([str(i) for i in range(1, 10)], k=8)))
    comment = db.Column(db.Text)
    publish_time = db.Column(db.DateTime, default=datetime.now)
    tread = db.Column(db.SmallInteger(), default=0)
    tcomment = db.Column(db.SmallInteger(), default=0)
    g_num = db.Column(db.Integer, default=0)
    l_num = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type_id = db.Column(db.Integer, db.ForeignKey('article_type.id'))

    def __str__(self):
        return self.t_name


class ArticleType(db.Model):
    __tablename__ = "article_type"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(10))
    t_article = db.relationship('Article', backref='type')


class Photo(db.Model):
    __tablename__ = "photo"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Vcomment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    v_name = db.Column(db.String(20), default='匿名用户')
    v_p_time = db.Column(db.DateTime, default=datetime.now)
    v_comment = db.Column(db.Text)
    v_con = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


class Collect(db.Model):
    __tablename__ = "collect"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))


class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    m_name = db.Column(db.String(16))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    m_con = db.Column(db.Text)