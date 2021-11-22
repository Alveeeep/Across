from flask import Flask, render_template
import unicodedata

from flask_wtf import CsrfProtect, CSRFProtect
from werkzeug.utils import redirect

from data import db_session
from flask import Flask, render_template, request, make_response, jsonify
from forms.search import SearchForm
from forms.login import LoginForm, RegisterForm
from forms.buy import BuyForm
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
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    return render_template('main_page.html', search_form=search_form)


@app.route('/search/<title>', methods=['GET', 'POST'])
def search(title):
    search_form = SearchForm()
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.title.like('%{}%'.format(title))).all()
    if len(items) == 0:
        items = db_sess.query(Item).filter(Item.name.like('%{}%'.format(title))).all()
    return render_template('shoes_page.html', items=items, length=len(items), title=title, search_form=search_form)


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


@app.route('/cart')  # корзина переименовать потом
def categories_page():
    db_sess = db_session.create_session()
    form = BuyForm()
    search_form = SearchForm()
    cart = []
    sizes = []
    items = []
    total = 0
    if search_form.validate_on_submit():
        res = search_form.search.data
        return redirect('/search/{}'.format(res))
    if current_user.is_authenticated:
        id = current_user.get_id()
        user = db_sess.query(User).filter(User.id == id).first()
        cart = user.cart
        cart = cart.split(', ')
    else:
        cart = request.cookies.get('usercart')
        cart = cart.split(',')
    for el in cart:
        el = el.split(':')
        id = int(el[0])
        sizes.append(int(el[1]))
        item = db_sess.query(Item).filter(Item.id == id).first()
        items.append(item)
        total += int(item.price)
    return render_template('cart_page.html', items=items, total=total, length=len(items), form=form,
                           search_form=search_form, sizes=sizes)


@app.route('/item_delete/<id>/<size>', methods=['GET', 'POST'])
def delete_item(id, size):
    db_sess = db_session.create_session()
    resp = make_response(redirect('/cart'))
    item_id = id
    if current_user.is_authenticated:
        id = current_user.get_id()
        user = db_sess.query(User).filter(User.id == id).first()
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
        cart = cart.split(',')
        for el in cart:
            if el == '{}:{}'.format(item_id, size):
                cart.remove(el)
        cart = ','.join(cart)
        resp.set_cookie('usercart', cart)
        return resp


@app.route('/categories/<title>', methods=['GET', 'POST'])
def shoes_page(title):
    db_sess = db_session.create_session()
    items = db_sess.query(Item).filter(Item.category == title).all()
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
    db_sess = db_session.create_session()
    item = db_sess.query(Item).filter(Item.id == item_id).first()
    images = item.image.split(', ')
    sizes = item.size.split(', ')
    resp = make_response(
        render_template('item_page.html', title=item.title, images=images, item=item, len=len(images), sizes=sizes,
                        form=form))
    if form.validate_on_submit():
        size = form.size.data
        if current_user.is_authenticated:
            id = current_user.get_id()
            user = db_sess.query(User).filter(User.id == id).first()
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
                    cookie += ',{}:{}'.format(item_id, size)
                    resp.set_cookie('usercart', cookie)
            else:
                resp.set_cookie('usercart', '{}:{}'.format(item_id, size))
        return resp
    return resp


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
