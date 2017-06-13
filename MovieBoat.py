from flask import render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import current_user, login_user, logout_user, LoginManager, login_required
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from models import db
from models import Movie, User, Comment, ChargeRecord, CustomRecord
from flask_app import app

from flask_moment import Moment

moment = Moment(app)


# migrate = Migrate(app, db)
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
# manager.run()







def init_login():
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.query(User).get(user_id)


@app.route('/')
def index():
    movies = Movie.query.all()

    return render_template('index.html', movies=movies, user=current_user)


@login_required
@app.route('/logout')
def logout():
    user = User.query.get(session.get('user_id'))
    logout_user()
    return redirect(url_for('.index'))


@login_required
@app.route('/charge')
def charge():
    return render_template('charge.html')


@login_required
@app.route('/user/history')
def history():
    custom_records = CustomRecord.query.filter_by(customer=current_user).all()

    return render_template('history.html', user=current_user, custom_records=custom_records)


@app.route('/login', methods=['POST'])
def login():
    print(request.form)
    phone = request.form.get('phone')
    password = request.form.get('password')

    user = User.query.filter_by(phone_number=phone).first()

    ret = {}

    if not user:
        ret['code'] = 101
        ret['message'] = '用户不存在'
        return jsonify(ret)

    if user.validate_password(password):
        ret['code'] = 100
        login_user(user)
    else:
        ret['code'] = 102
        ret['message'] = '密码错误'

    return jsonify(ret)


@app.route('/movie/<movie_id>', methods=['GET'])
def movie_detail(movie_id):
    movie = Movie.query.filter_by(brief_id=movie_id).first()
    if not movie:
        abort(404)

    comments = Comment.query.filter_by(movie=movie)

    return render_template('movie_detail.html', movie=movie, user=current_user, comments=comments)


@app.route('/watch/<movie_id>', methods=['GET'])
def watch(movie_id):
    movie = Movie.query.filter_by(brief_id=movie_id).first()
    if not movie:
        abort(404)
    return render_template('watch.html', movie=movie, user=current_user)


@login_required
@app.route('/profile/', methods=['GET'])
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword')

    movies = Movie.query.filter(Movie.title.like('%' + keyword + '%')).all()

    return render_template('index.html', user=current_user, movies=movies, keyword=keyword)


@app.route('/register', methods=['POST'])
def register():
    print(request.form)
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    print(username, password, phone)
    # avatar=request.files
    ret = {}

    user = User.query.filter_by(phone_number=phone).first()
    if user:
        ret['code'] = 201
        ret['message'] = '此手机已经被注册'
        return jsonify(ret)

    user = User.query.filter_by(username=username).first()
    if user:
        ret['code'] = 202
        ret['message'] = '此用户名已经被注册'
        return jsonify(ret)

    user = User(
        username=username,
        phone_number=phone,
        password=password
    )
    db.session.add(user)
    db.session.commit()

    login_user(user)

    ret['code'] = 200
    ret['message'] = '注册成功'

    return jsonify(ret)


if __name__ == '__main__':
    init_login()
    app.run(debug=True)
