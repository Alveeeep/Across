from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired


class Cart(FlaskForm):
    size = TextAreaField()
    submit = SubmitField("В корзину")