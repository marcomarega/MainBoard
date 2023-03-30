import math
import threading
from datetime import datetime, time, timedelta
from time import sleep

from flask import Flask, render_template
from data import db_session
from data.costs import Cost
from data.promos import Promo

app = Flask(__name__)
last_cost = 0


@app.route("/")
def index():
    db_sess = db_session.create_session()
    costs = db_sess.query(Cost).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
    return render_template("index.html", title="MainBoard", costs=costs, promos=db_sess.query(Promo)[:20])


def cost_counter():
    global last_cost
    base_cost = 80
    iters = 0
    db_sess = db_session.create_session()
    while True:
        promos = db_sess.query(Promo).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
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
        sleep(5)


if __name__ == "__main__":
    db_session.global_init("db/main_board.db")

    db_sess = db_session.create_session()
    promo = Promo(
        header='Google',
        text='New Google Pixel!',
        cost=1900,
        organization_id=1,
    )
    db_sess.add(promo)
    db_sess.commit()

    thr = threading.Thread(target=cost_counter)
    thr.start()
    app.run(host="127.0.0.1", port=8080)
