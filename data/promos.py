import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from .organizations import Organization


class Promo(SqlAlchemyBase):
    __tablename__ = 'promos'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    header = sqlalchemy.Column(sqlalchemy.String)
    text = sqlalchemy.Column(sqlalchemy.String)
    cost = sqlalchemy.Column(sqlalchemy.Float)
    organization_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey(Organization.id))
    organization = orm.relationship(Organization)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
