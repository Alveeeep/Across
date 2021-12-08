from flask import Flask, render_template, request, make_response, jsonify
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy, Model
import unicodedata
from flask_wtf import CsrfProtect, CSRFProtect
from werkzeug.utils import redirect
from forms.search import SearchForm
from forms.login import LoginForm, RegisterForm
from forms.buy import BuyForm
from forms.cart import Cart
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.models import db
import json
import math

app = Flask(__name__)
app.app_context().push()
db.init_app(app)
CSRFProtect(app)
app.config['SECRET_KEY'] = 'across_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)

from data.models import User, Item, New


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['POST', 'GET'])
def main_page():
    news = New.query.all()
    items = []
    print(news)
    for el in news:
        item = Item.query.filter(Item.id == el.id).first()
        items.append(item)
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    return render_template('main_page.html', search_form=search_form, news=items, length=len(items))


@app.route('/search/<title>', methods=['GET', 'POST'])
def search(title):
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    items = Item.query.filter(Item.title.like('%{}%'.format(title))).all()
    if len(items) == 0:
        items = Item.query.filter(Item.name.like('%{}%'.format(title))).all()
    return render_template('shoes_page.html', items=items, length=len(items), title=title, search_form=search_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    form_signup = RegisterForm()
    if form_login.validate_on_submit():
        user = User.query.filter(User.email == form_login.email.data).first()
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
        if User.query.filter(User.email == form_signup.email.data).first():
            return render_template('login.html', signup_form=form_signup, login_form=form_login,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form_signup.name.data,
            email=form_signup.email.data,
            phone=form_signup.phone.data
        )
        user.set_password(form_signup.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('login.html', signup_form=form_signup, login_form=form_login)


@app.route('/cart', methods=['GET', 'POST'])  # корзина переименовать потом
def categories_page():
    form = BuyForm()
    cart = []
    sizes = []
    items = []
    total = 0
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    if current_user.is_authenticated:
        id = current_user.get_id()
        user = User.query.filter(User.id == id).first()
        cart = user.cart
    else:
        cart = request.cookies.get('usercart')
    if len(cart) != 0:
        cart = cart.split(', ')
        for el in cart:
            el = el.split(':')
            id = int(el[0])
            sizes.append(int(el[1]))
            item = Item.query.filter(Item.id == id).first()
            items.append(item)
            total += int(item.price)
        return render_template('cart_page.html', items=items, total=total, length=len(items), form=form,
                               search_form=search_form, sizes=sizes)
    else:
        return render_template('cart_page.html', length=0, search_form=search_form)


@app.route('/item_delete/<id>/<size>', methods=['GET', 'POST'])
def delete_item(id, size):
    resp = make_response(redirect('/cart'))
    item_id = id
    if current_user.is_authenticated:
        id = current_user.get_id()
        user = User.query.filter(User.id == id).first()
        cart = user.cart
        cart = cart.split(', ')
        for el in cart:
            if el == '{}:{}'.format(item_id, size):
                cart.remove(el)
        user.cart = ', '.join(cart)
        db_sess.commit()
        return resp
    else:
        cart = request.cookies.get('usercart')
        cart = cart.split(', ')
        for el in cart:
            if el == '{}:{}'.format(item_id, size):
                cart.remove(el)
        cart = ','.join(cart)
        resp.set_cookie('usercart', cart)
        return resp


@app.route('/categories/<title>', methods=['GET', 'POST'])
def shoes_page(title):
    items = Item.query.filter(Item.category == title).all()
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    with open("static/json/categories.json", "rt", encoding="utf8") as f:
        c_list = json.loads(f.read())
    c = c_list[title]
    return render_template('shoes_page.html', items=items, length=len(items), title=c, search_form=search_form)


@app.route('/items/<item_id>', methods=['GET', 'POST'])
def item_page(item_id):
    form = Cart()
    item = Item.query.filter(Item.id == item_id).first()
    images = item.image.split(', ')
    sizes = item.size.split(', ')
    resp = make_response(
        render_template('item_page.html', title=item.title, images=images, item=item, len=len(images), sizes=sizes,
                        form=form))
    if form.validate_on_submit():
        size = form.size.data
        if current_user.is_authenticated:
            id = current_user.get_id()
            user = User.query.filter(User.id == id).first()
            cart = user.cart
            if len(cart) != 0:
                cart += ', {}:{}'.format(item_id, size)
                user.cart = cart
                db_sess.commit()
            else:
                user.cart = '{}:{}'.format(item_id, size)
                db_sess.commit()
        else:
            cookie = request.cookies.get('usercart')
            if cookie is not None:
                if '{}:{}'.format(item_id, size) not in cookie:
                    cookie += ', {}:{}'.format(item_id, size)
                    resp.set_cookie('usercart', cookie)
            else:
                resp.set_cookie('usercart', '{}:{}'.format(item_id, size))
        return resp
    return resp


def main():
    app.run()


if __name__ == '__main__':
    main()
