from flask import Blueprint, render_template, request, g, url_for, session, jsonify
from werkzeug.utils import redirect

from app.user.models import Article, User, Vcomment, Collect, Message
from ext import db

article_app = Blueprint('article', __name__)


def userinfo():
    uid = session['uid']
    user = User.query.filter_by(id=uid).first()
    g.name = user.name
    g.icon = user.icon
    g.id = user.id


@article_app.route('/detail', methods=['GET', 'POST'])
def detail():
    if request.method == 'POST':
        username = request.form.get('username')
        c_name = request.form.get('c_name')
        ocomment = request.form.get('ocomment')
        a_id = request.form.get('a_id')
        print(username, c_name, ocomment, a_id)

        article = Article.query.filter_by(id=a_id).first()
        userinfo()
        comments = Vcomment.query.filter_by(user_id=a_id)

        # 数据校验
        if not all([username, c_name, ocomment, a_id]):
            return render_template('detail.html', article=article, comments=comments, msg='数据不完整')

        article = Article.query.filter_by(id=a_id).first()
        if not article:
            return render_template('detail.html', article=article, comments=comments, msg='文章错误')

        u = User.query.filter_by(name=username).first()
        if not u:
            return render_template('detail.html', article=article, comments=comments, msg='评论对象不存在')

        # v = Vcomment.query.filter_by(v_name=c_name).all()
        # if not v:
        #     return render_template('detail.html', article=article, comments=comments, msg='用户未登录')

        # 信息写入数据库
        vc = Vcomment()
        vc.user_id = u.id
        vc.v_comment = ocomment
        vc.v_con = u.icon
        vc.v_name = c_name
        vc.article_id = a_id

        db.session.add(vc)
        db.session.commit()

        return redirect(url_for('article.detail') + '?a_id=' + a_id)

    a_id = request.args.get('a_id')
    article = Article.query.filter_by(id=a_id).first()
    print('============>', '浏览的文章')
    article.tread = article.tread + 1
    db.session.add(article)
    db.session.commit()

    # if not art.tread:
    #     art.tread = 0
    # art.tread = int(art.tread) + 1
    # db.session.commit(art)
    userinfo()
    comments = Vcomment.query.filter_by(article_id=a_id)

    # 查看是否该用户收藏过的文章
    uid = session['uid']
    collect = Collect.query.filter_by(user_id=uid, article_id=a_id).first()

    return render_template('detail.html', article=article, comments=comments, collect=collect)


@article_app.route('/change', methods=['POST'])
def change():
    a_id = request.form.get('ar_id')
    c_tar = request.form.get('c_tar')

    print(c_tar)

    if not all([a_id, c_tar]):
        return jsonify({'res': 0, 'msg': '数据不完整'})

    article = Article.query.filter_by(id=a_id).first()
    if not article:
        return jsonify({'res': 1, 'msg': '文章不存在'})

    uid = session['uid']

    if c_tar == '0':
        article.g_num = int(article.g_num) + 1
    if c_tar == '1':
        article.l_num = int(article.l_num) + 1
        collect = Collect(user_id=uid, article_id=a_id)
        db.session.add(collect)
    if c_tar == '2':
        article.l_num = int(article.l_num) - 1
        collect = Collect.query.filter_by(user_id=uid, article_id=a_id).first()
        print('走了')
        db.session.delete(collect)

    db.session.add(article)
    db.session.commit()
    return jsonify({'res': 2})


@article_app.route('/leave', methods=['GET','POST'])
def leave():
    if request.method == "POST":
        m_name = request.form.get('m_name')
        user_id = request.form.get('user_id')
        leave = request.form.get('leave')
        print(m_name, user_id, leave)

        # 校验
        buser = User.query.filter_by(id=user_id).first()
        if not buser:
            return render_template('givemessage.html', msg='不存在该用户')

        if not leave:
            return render_template('givemessage.html', msg='留言内容为空')

        me = Message(user_id=user_id, m_name=m_name, m_con=leave)
        db.session.add(me)
        db.session.commit()
        userinfo()
        return render_template('givemessage.html', msg='留言成功')
    userinfo()
    return render_template('givemessage.html')


@article_app.route('/man', methods=['GET','POST'])
def manager():
    if request.method == 'POST':
        a_id = request.form.get('art_id')

        if not a_id:
            return jsonify({'res': 1, 'msg': '参数错误'})

        article = Article.query.filter_by(id=a_id).first()
        if not article:
            return jsonify({'res': 2, 'msg': '文章不存在'})

        # 业务处理
        db.session.delete(article)
        db.session.commit()

        # 返回应答
        return jsonify({'res': 0, 'msg': '删除成功'})

    articles = Article.query.all()
    userinfo()
    return render_template('manager.html', articles=articles)
