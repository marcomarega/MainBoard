import datetime
import sqlalchemy
from flask_wtf import FlaskForm
from sqlalchemy import orm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from .db_session import SqlAlchemyBase
from .organizations import Organization
from .sites import Site


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
    verified = sqlalchemy.Column(sqlalchemy.Boolean,
                                 default=False)
    published = sqlalchemy.Column(sqlalchemy.Boolean,
                                  default=False)


class AddPromoForm(FlaskForm):
    header = StringField("Title", validators=[DataRequired()])
    text = StringField("Text", validators=[DataRequired()])
    submit = SubmitField("Add promo")


class PromoView(SqlAlchemyBase):
    __tablename__ = 'promo_views'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    ip_address = sqlalchemy.Column(sqlalchemy.String, index=True)

    promo_id = sqlalchemy.Column(sqlalchemy.Integer,
                                 sqlalchemy.ForeignKey(Promo.id))
    promo = orm.relationship(Promo, foreign_keys=[promo_id])

    site_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey(Site.id))
    site = orm.relationship(Site, foreign_keys=[site_id])

    date = sqlalchemy.Column(sqlalchemy.DateTime,
                             default=datetime.datetime.now)
