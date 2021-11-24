import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class New(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)