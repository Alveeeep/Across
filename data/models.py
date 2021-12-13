from flask_sqlalchemy import SQLAlchemy, Model
import datetime
from flask_login import UserMixin
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String,
                      index=True, unique=True, nullable=True)
    phone = db.Column(db.String, nullable=True)
    hashed_password = db.Column(db.String, nullable=True)
    created_date = db.Column(db.DateTime,
                             default=datetime.datetime.now)
    cart = db.Column(db.String, nullable=True)
    total = db.Column(db.Integer, nullable=True)
    role = db.Column(db.String, nullable=True)
    active = db.Column(db.Boolean())

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Item(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=True)
    name = db.Column(db.String, nullable=True)
    about = db.Column(db.String, nullable=True)
    price = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String, nullable=True)
    image = db.Column(db.String, nullable=True)
    show_img = db.Column(db.String, nullable=True)
    color = db.Column(db.String, nullable=True)
    size = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)

    def __repr__(self):
        return "<Item> {}, price - {}, category - {}".format(self.title, self.price, self.category)


class New(db.Model):
    id = db.Column(db.Integer,
                   primary_key=True, autoincrement=True)
