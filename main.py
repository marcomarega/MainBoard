import math
import threading
from datetime import datetime, time, timedelta
from time import sleep

from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session
from data.costs import Cost
from data.promos import Promo
from data.users import User, RegistrationForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '>#s!-R>yAI0M4%dpsQQ>6(!h{ljfIsdPBk`}82[,z|7:SOOHn<^yj6R@xH*fRj@'
login_manager = LoginManager()
login_manager.init_app(app)

last_cost = 0


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    costs = db_sess.query(Cost).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
    username = "Guest"
    if current_user.is_authenticated:
        username = current_user.username
    return render_template("index.html", title="MainBoard", costs=costs, promos=db_sess.query(Promo)[::-1][:20],
                           username=username)


@app.route("/promo_table")
def promo_table():
    db_sess = db_session.create_session()
    return render_template("promo_table.html", promos=db_sess.query(Promo)[::-1][:5])


@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    username = "Guest"
    if current_user.is_authenticated:
        username = current_user.username
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("form.html", title="Registration", message=f"User with email {form.email.data}"
                                                                              f" already exists", form=form,
                                   username=username)
        if form.password.data != form.password_again.data:
            return render_template("form.html", title="Registration", message="Passwords do not match", form=form,
                                   username=username)
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("form.html", title="Registration", form=form,
                           username=username)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    username = "Guest"
    if current_user.is_authenticated:
        username = current_user.username
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("form.html", title="Login", message="Wrong email or password", form=form,
                               username=username)
    return render_template("form.html", title="Login", form=form,
                           username=username)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


def cost_counter():
    global last_cost
    base_cost = 1000
    iters = 0
    db_sess = db_session.create_session()
    while True:
        promos = db_sess.query(Promo, ).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
        current_cost = base_cost
        for promo in promos:
            b = base_cost
            c = promo.cost
            t = math.sqrt(c + b ** 2)
            x = (datetime.now() - promo.created_date).seconds
            current_cost += round(max(0., -(x + 1) ** math.log(x + 1, t) + c + 1), 2)
        cost = Cost(
            value=current_cost
        )
        db_sess.add(cost)
        db_sess.commit()
        last_cost = current_cost
        if iters % 100 == 0:
            promo = Promo(
                header=f'Conpany no.{iters}',
                text='TRY OUR NEW COOL PRODUCT',
                cost=last_cost,
                organization_id=iters,
            )
            db_sess.add(promo)
            db_sess.commit()
        iters += 1
        sleep(5)


if __name__ == "__main__":
    db_session.global_init("db/main_board.db")

    thr = threading.Thread(target=cost_counter)
    thr.start()
    app.run(host="127.0.0.1", port=8080)
