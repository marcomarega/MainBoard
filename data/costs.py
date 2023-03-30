import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Cost(SqlAlchemyBase):
    __tablename__ = 'costs'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    value = sqlalchemy.Column(sqlalchemy.Float)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now, index=True)
