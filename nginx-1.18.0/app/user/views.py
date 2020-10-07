import re

from flask import Blueprint, render_template, request, g, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from app.user.models import Article, ArticleType, User, Photo, Message, Collect
from ext import db
from setting import base

user_app = Blueprint('user', __name__)

TYPE = {
    '0': '全部',
    '1': '随笔',
    '2': '生活',
    '3': '程序人生',
    '4': '音乐',
    '5': '其他',
}

TYPE1 = {
    '全部': '0',
    '随笔': '1',
    '生活': '2',
    '程序人生': '3',
    '音乐': '4',
    '其他': '5'
}

request_login_list = ['/', '/center', '/cen', '/aboutme', '/index', '/message', '/photo',
                      '/publish', '/show_me', '/show_photo', '/show_collect', '/givemessage']


# 用户权限验证
@user_app.before_app_first_request
def before_app_first_request():
    print('======> before_app_first_request')


@user_app.before_app_request
def before_app_request():
    print('=========> before_app_request', request.path)

    # 验证
    if request.path in request_login_list:
        try:
            uid = session['uid']
            user = User.query.filter_by(id=uid).first()
            types = ArticleType.query.all()
            mes_num = len(user.message)
            g.name = user.name
            g.icon = user.icon
            g.types = types
            g.message = mes_num

        except Exception as e:
            render_template('login.html')


@user_app.route('/', methods=['GET', 'POST'])
@user_app.route('/index', methods=['GET', 'POST'], endpoint='index')
def index():
    type = request.args.get('type', '0')
    page = request.args.get('page', '1')
    tar = request.args.get('num')
    pages = request.args.get('pages')

    print(tar)
    if tar == 'prev':
        page = 1
    elif tar == 'next':
        page = pages
    page = int(page)

    types = ArticleType.query.all()

    if type == '0':
        paginates = Article.query.order_by(-Article.publish_time).paginate(page=page, per_page=2)

    else:
        paginates = Article.query.filter_by(type_id=type).order_by(-Article.publish_time).paginate(page=page,
                                                                                                   per_page=2)

    g.n = Article.query.count()
    g.tid = type

    try:
        uid = session['uid']
    except:
        return redirect(url_for('user.login'))

    a_n = Article.query.all()
    a_n_1 = Article.query.first()
    for a in a_n[1:]:
        a_n_1.g_num += a.g_num
    g.g_num = a_n_1.g_num

    a_n = Article.query.all()
    a_n_1 = Article.query.first()
    for a in a_n[1:]:
        a_n_1.tread += a.tread
    g.tread = a_n_1.tread

    # print(paginates)
    # print(paginates.items)  # 每一页的有多少对象
    # print(paginates.page)   # 传给模板的页数
    # print(paginates.pages)  # 总页数
    # print(page_num)         # 当前页

    return render_template('index.html', paginates=paginates, types=types, ptype=TYPE[str(type)])


@user_app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')

        # 数据校验
        if not all([username, password, repassword, phone, email]):
            return render_template('register.html', msg='数据不完整')

        try:
            user = User.query.filter_by(user=username)
        except:
            return render_template('register.html', msg='该用户已经注册过了')

        if password != repassword:
            return render_template('register.html', msg='两次密码不一致')

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render_template('register.html', msg='邮箱错误')

        if not re.match(r'^(13[0-9]|14[5|7]|15[0|1|2|3|5|6|7|8|9]|18[0|1|2|3|5|6|7|8|9])\d{8}$', phone):
            return render_template('register.html', msg='电话错误')

        # 密码加密
        password = generate_password_hash(password)

        # 创建数据
        user = User(name=username, password=password, phone=phone, email=email)

        # 写入数据库
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('user.login'))
    return render_template('register.html')


@user_app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 数据校验
        if not all([username, password]):
            return render_template('login.html', msg='数据不完整')

        try:
            user = User.query.filter(User.name == username).first()
        except:
            return render_template('login.html', msg='该用户未注册')

        if not check_password_hash(user.password, password):
            return render_template('login.html', msg='密码错误')

        session['uid'] = user.id

        return redirect(url_for('.index'))
    return render_template('login.html')


@user_app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone = request.form.get('phone')
    verify = request.form.get('verify')
    print(phone, verify)
    return render_template('index.html')


@user_app.route('/center', methods=['GET', 'POST'])
def center():
    types = ArticleType.query.all()
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        phone = request.form.get('phone')
        email = request.form.get('email')
        icon = request.files['thum']

        if repassword != password:
            return render_template('center-info.html', msg='两次密码不一致')

        # 判断图片格式是否正确
        fix = icon.filename.split('.')[-1]
        if fix not in ['jpg', 'png', 'dmp']:
            return render_template('center-info.html', msg='图片格式错误')

        # 本地保存图片
        icon.save(base + '/static/img/upload_icon/' + icon.filename)

        # TODO 七牛云图片上传

        # 获取对象
        uid = session['uid']
        user = User.query.filter_by(id=uid).first()

        # 写入数据库
        if name:
            user.name = name
        if password:
            user.password = password
        if phone:
            user.phone = phone
        if email:
            user.email = email
        if icon:
            user.icon = '/static/img/upload_icon/' + icon.filename

        db.session.commit()
        return render_template('center-info.html', msg='修改成功')

    return render_template('center-info.html', types=types)


@user_app.route('/cen', methods=['GET'])
def cen():
    return render_template('center.html')


@user_app.route('/publish', methods=['GET', 'POST'])
def publish():
    if request.method == 'POST':
        title = request.form.get('title')
        type = request.form.get('type')
        print(type)
        content = request.form.get('content')
        types = ArticleType.query.all()

        # 数据校验
        if not all([title, type, content]):
            return render_template('publish.html', types=types, msg='数据不完整')

        if type not in TYPE1.keys():
            return render_template('publish.html', types=types, msg='非法类型')

        # 创建对象
        uid = session['uid']
        article = Article(t_name=title, comment=content, user_id=uid, type_id=TYPE1[type])
        db.session.add(article)
        db.session.commit()
        return render_template('publish.html', types=types, msg='发布成功')

    types = ArticleType.query.all()
    return render_template('publish.html', types=types)


@user_app.route('/photo', methods=['GET', 'POST'])
def photo():
    uid = session['uid']
    if request.method == 'POST':
        tar = request.form.get('tar')
        print(tar)
        if tar == '0':
            photo = request.files['photo']

            if not photo:
                return render_template('photo.html', msg='图片无效')

            # 判断图片格式是否正确
            fix = photo.filename.split('.')[-1]
            if fix not in ['jpg', 'png', 'dmp']:
                return render_template('photo.html', msg='图片格式错误')

            # 本地保存图片
            photo.save(base + '/static/img/upload_photo/' + photo.filename)

            ph = Photo(name='/static/img/upload_photo/' + photo.filename, user_id=uid)
            db.session.add(ph)
            db.session.commit()

            return redirect(url_for('user.photo'))
        elif tar == '1':
            pid = request.form.get('pid')
            photos = Photo.query.filter_by(user_id=uid).all()
            if not pid:
                return render_template('photo.html', photos=photos, msg='图片错误')
            p = Photo.query.filter_by(id=pid).first()
            print(p)
            if not p:
                return render_template('photo.html', photos=photos, msg='图片信息错误')
            db.session.delete(p)
            db.session.commit()
            return jsonify({'res': 1, 'msg': '删除成功'})

    photos = Photo.query.filter_by(user_id=uid).all()
    return render_template('photo.html', photos=photos)


@user_app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        m_id = request.form.get('m_id')

        # 校验参数
        if not m_id:
            return jsonify({'res': 0, 'msg': '参数错误'})

        m = Message.query.filter_by(id=m_id).first()
        if not m:
            return jsonify({'res': 1, 'msg': '无效留言'})

        # 业务操作
        db.session.delete(m)
        db.session.commit()
        return jsonify({'res': 2, 'msg': '删除成功'})

    uid = session['uid']
    # message = Message.query.filter_by(user_id=uid).all()

    user = User.query.filter_by(id=uid).first()
    g.m_n = Message.query.count()
    messages = Message.query.filter_by(user_id=uid).all()
    print(message)
    return render_template('message.html', messages=messages)


@user_app.route('/aboutme', methods=['GET', 'POST'])
def aboutme():
    if request.method == 'POST':
        content = request.form.get('content')
        print(content)
        # 校验
        if not content:
            return render_template('aboutme.html', msg='无内容保存')

        uid = session['uid']
        user = User.query.filter_by(id=uid).first()
        user.abe = content

        db.session.commit()
        return render_template('aboutme.html', msg='保存成功')
    return render_template('aboutme.html')


@user_app.route('/show_photo', methods=['GET'])
def show_photo():
    uid = session['uid']
    user = User.query.filter_by(id=uid).first()
    photos = user.photo
    return render_template('show_photo.html', photos=photos)


@user_app.route('/collect', methods=['GET', 'POST'])
def collect():
    if request.method == 'POST':
        c_id = request.form.get('c_id')

        # 检验
        if not c_id:
            return jsonify({'res': 0, 'msg': '参数错误'})

        colloct = Collect.query.filter_by(article_id=c_id).first()
        print(colloct)
        if not colloct:
            return jsonify({'res': 1, 'msg': '收藏文章不存在'})

        # 业务处理
        collect = Collect(article_id=c_id)
        db.session.delete(colloct)
        db.session.commit()

        return jsonify({'res': 2, 'msg': '取消成功'})

    l = []
    uid = session['uid']
    user = User.query.filter_by(id=uid).first()
    collects = user.collect

    for i in collects:
        print(i)
        ar = Article.query.filter_by(id=i.article_id).first()

        l.append(ar)
    return render_template('collect.html', collects=l)


@user_app.route('/show_me', methods=['GET'])
def show_me():
    uid = session['uid']
    user = User.query.filter_by(id=uid).first()
    g.info = user.abe
    print(user.abe)
    return render_template('show_me.html')


@user_app.route('/logout')
def logout():
    del session['uid']
    return render_template('login.html')
