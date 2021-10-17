from flask import Flask, render_template
import unicodedata

from flask_wtf import CsrfProtect, CSRFProtect
from werkzeug.utils import redirect

from data import db_session
from flask import Flask, render_template, request
from forms.search import SearchForm
from forms.login import LoginForm, RegisterForm
from data.users import User
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


@app.route('/')
def main_page():
    return render_template('main_page.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    form_signup = RegisterForm()
    if request.method == 'POST':
        form_name = request.form['form-name']
        if form_name == 'login':
            return render_template('login.html', form=form_login)
        elif form_name == 'signup':
            return render_template('login.html', form=form_signup)

@app.route('/categories')
def categories_page():
    return render_template('categories_page.html')


@app.route('/new')
def new_page():
    return render_template('new_page.html')


@app.route('/categories/shoes')
def shoes_page():
    return render_template('shoes_page.html')


@app.route('/categories/clothes')
def clothes_page():
    return render_template('clothes_page.html')


@app.route('/categories/custom')
def custom_page():
    return render_template('custom_page.html')


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
