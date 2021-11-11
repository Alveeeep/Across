from flask import Flask, render_template
import unicodedata

from flask_wtf import CsrfProtect, CSRFProtect
from werkzeug.utils import redirect

from data import db_session
from flask import Flask, render_template, request
from forms.search import SearchForm
from forms.login import LoginForm, RegisterForm
from forms.cart import Cart
from data.users import User
from data.items import Item
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import json
import math

app = Flask(__name__)
CSRFProtect(app)
app.config['SECRET_KEY'] = 'across_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['POST', 'GET'])
def main_page():
    return render_template('main_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    form_signup = RegisterForm()
    if form_login.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form_login.email.data).first()
        if user and user.check_password(form_login.password.data):
            login_user(user)
            return redirect('/')
        return render_template('login.html', signup_form=form_signup, login_form=form_login,
                               message="Неправильный логин или пароль")
    return render_template('login.html', signup_form=form_signup, login_form=form_login)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form_login = LoginForm()
    form_signup = RegisterForm()
    if form_signup.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form_signup.email.data).first():
            return render_template('login.html', signup_form=form_signup, login_form=form_login,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form_signup.name.data,
            email=form_signup.email.data,
            phone=form_signup.phone.data
        )
        user.set_password(form_signup.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('login.html', signup_form=form_signup, login_form=form_login)


@app.route('/categories')  # корзина переименовать потом
def categories_page():
    return render_template('categories_page.html')


@app.route('/categories/<title>', methods=['GET', 'POST'])
def shoes_page(title):
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.category == title).all()
    with open("static/json/categories.json", "rt", encoding="utf8") as f:
        c_list = json.loads(f.read())
    c = c_list[title]
    return render_template('shoes_page.html', items=items, length=len(items), title=с)


@app.route('/items/<item_id>', methods=['GET', 'POST'])
def item_page(item_id):
    form = Cart()
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == item_id).first()
    images = item.image.split(', ')
    sizes = item.size.split(', ')
    return render_template('item_page.html', title=item.title, images=images, item=item, len=len(images), sizes=sizes)


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
