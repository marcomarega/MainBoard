import datetime
import sqlalchemy
from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, EmailField, SubmitField
from wtforms.validators import DataRequired, URL

from .db_session import SqlAlchemyBase
from .users import User


class Organization(SqlAlchemyBase):
    __tablename__ = 'organizations'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    url = sqlalchemy.Column(sqlalchemy.String, unique=True, index=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey(User.id))
    user = orm.relationship(User)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    verified = sqlalchemy.Column(sqlalchemy.Boolean,
                                 default=False)


class AddOrganizationForm(FlaskForm):
    name = StringField("Organization name", validators=[DataRequired()])
    url = StringField("Organization URL", validators=[URL()])
    submit = SubmitField("Add organization", validators=[DataRequired()])
