from flask import Flask, render_template, abort, request
from werkzeug.utils import redirect

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.news import News
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm
from data.users import User
from data.book import Book
from data.games import Game
from data.humor import Humo
from data.film import Film


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/blogs.db")
    app.run()




@app.route("/")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) |
            (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html",
                           news=news)


@app.route("/humor")
def humor():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Humo).filter(
            (Humo.user == current_user) |
            (Humo.is_private != True))
    else:
        news = db_sess.query(Humo).filter(Humo.is_private != True)
    return render_template("humor.html",
                           news=news)

@app.route("/game")
def game():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Game).filter(
            (Game.user == current_user) |
            (Game.is_private != True))
    else:
        news = db_sess.query(Game).filter(Game.is_private != True)
    return render_template("games.html",
                           news=news)

@app.route("/book")
def book():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Book).filter(
            (Book.user == current_user) |
            (Book.is_private != True))
    else:
        news = db_sess.query(Book).filter(Book.is_private != True)
    return render_template("book.html",
                           news=news)

@app.route("/film")
def films():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(Film).filter(
            (Film.user == current_user) |
            (Film.is_private != True))
    else:
        news = db_sess.query(Film).filter(Film.is_private != True)
    return render_template("film.html",
                           news=news)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html',
                           title='Регистрация',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user,
                       remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)

    return render_template('login.html',
                           title='Авторизация',
                           form=form)




@app.route('/logout')
def logout():
    logout_user()
    return redirect("/")


@app.route('/news',  methods=['GET', 'POST'])
def add_news():
    form = NewsForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')

    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))

    else:
        news = db_sess.query(News).filter(News.is_private != True)

    return render_template('news.html',
                           form=form,
                           news=news)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()

        if news:
            form.content.data = news.content
            form.is_private.data = news.is_private

        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()

        if news:
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/')

        else:
            abort(404)

    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()

    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()

    if news:
        db_sess.delete(news)
        db_sess.commit()

    else:
        abort(404)
    return redirect('/')


@app.route('/films', methods=['GET', 'POST'])
def add_film():
    form = NewsForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = Film()
        news.content = form.content.data
        print(1)
        news.is_private = form.is_private.data
        current_user.films.append(news)
        print(2)
        db_sess.merge(current_user)
        db_sess.commit()
        print(2)
        return redirect('/film')

    db_sess = db_session.create_session()

    if current_user.is_authenticated:
        news = db_sess.query(Film).filter(
            (Film.user == current_user) | (Film.is_private != True))

    else:
        news = db_sess.query(Film).filter(Film.is_private != True)
    print(3)
    return render_template('news.html',
                           form=form,
                           news=news)


@app.route('/films/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
    form = NewsForm()

    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(Film).filter(Film.id == id,
                                          Film.user == current_user
                                          ).first()

        if news:
            form.content.data = news.content
            form.is_private.data = news.is_private

        else:
            abort(404)

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(Film).filter(Film.id == id,
                                          Film.user == current_user
                                          ).first()

        if news:
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/film')

        else:
            abort(404)

    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/film_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def film_delete(id):
    db_sess = db_session.create_session()

    news = db_sess.query(Film).filter(Film.id == id,
                                      Film.user == current_user
                                      ).first()

    if news:
        db_sess.delete(news)
        db_sess.commit()

    else:
        abort(404)
    return redirect('/film')





if __name__ == '__main__':
    main()