import datetime
import sqlalchemy
from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL

from .db_session import SqlAlchemyBase
from .users import User


class Site(SqlAlchemyBase):
    __tablename__ = 'sites'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    url = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    key = sqlalchemy.Column(sqlalchemy.String)
    total_income = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    balance = sqlalchemy.Column(sqlalchemy.Float, default=0.0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey(User.id))
    user = orm.relationship(User)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    verified = sqlalchemy.Column(sqlalchemy.Boolean,
                                 default=False)


class AddSiteForm(FlaskForm):
    name = StringField("Site name", validators=[DataRequired()])
    url = StringField("URL", validators=[DataRequired(), URL()])
    submit = SubmitField("Add site", validators=[DataRequired()])
