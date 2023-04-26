import math
import threading
from datetime import datetime, time, timedelta
from time import sleep

from flask import Flask, render_template, redirect, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session
from data.costs import Cost
from data.organizations import Organization, AddOrganizationForm
from data.promos import Promo, PromoView, AddPromoForm
from data.sites import AddSiteForm, Site
from data.users import User, RegistrationForm, LoginForm
from functions import random_key_gen

app = Flask(__name__)
app.config['SECRET_KEY'] = '>#s!-R>yAI0M4%dpsQQ>6(!h{ljfIsdPBk`}82[,z|7:SOOHn<^yj6R@xH*fRj@'
login_manager = LoginManager()
login_manager.init_app(app)

last_cost = 0


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.get_session()
    result = db_sess.query(User).get(user_id)
    return result


@app.route("/_stuff", methods=["GET"])
def stuff():
    db_sess = db_session.get_session()
    costs = db_sess.query(Cost).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
    return jsonify(costs=costs)


@app.route("/")
def index():
    db_sess = db_session.get_session()
    costs = db_sess.query(Cost).filter(Cost.created_date >= datetime.now() - timedelta(days=1))
    result = render_template("index.html", title="MainBoard", costs=costs,
                             promos=db_sess.query(Promo).filter(Promo.published == True)[::-1][:20],
                             current_user=current_user)
    return result


@app.route("/promo_table/<site_key>")
def promo_table(site_key):
    db_sess = db_session.get_session()
    if not db_sess.query(Site).filter(Site.key == site_key).first():
        return
    ip_address = request.remote_addr
    promos = db_sess.query(Promo).filter(Promo.published == True)[::-1]
    promo = None
    if len(promos) > 0:
        promo = promos[0]
    site = None
    if promo is not None and db_sess.query(PromoView).filter(PromoView.promo_id == promo.id,
                                                                   PromoView.ip_address == ip_address,
                                                                   PromoView.date >=
                                                                   datetime.now() - timedelta(minutes=4)).first() is None:
        site = db_sess.query(Site).filter(Site.key == site_key).first()
        promo_view = PromoView(
            site=site,
            promo=promo,
            ip_address=ip_address
        )
        db_sess.add(promo_view)
    promo = None
    if len(promos) > 1:
        promo = promos[1]
    if promo is not None and db_sess.query(PromoView).filter(PromoView.promo_id == promo.id,
                                                                   PromoView.ip_address == ip_address,
                                                                   PromoView.date >=
                                                                   datetime.now() - timedelta(minutes=4)).first() is None:
        site = db_sess.query(Site).filter(Site.key == site_key).first()
        promo_view = PromoView(
            site=site,
            promo=promo,
            ip_address=ip_address
        )
        db_sess.add(promo_view)
    db_sess.commit()
    result = render_template("promo_table.html", promos=promos[:5])
    return result


@app.route("/registration", methods=["GET", "POST"])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.get_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template("form.html", title="Registration", message=f"User with email {form.email.data}"
                                                                              f" already exists", form=form,
                                   current_user=current_user)
        if form.password.data != form.password_again.data:
            return render_template("form.html", title="Registration", message="Passwords do not match", form=form,
                                   current_user=current_user)
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("form.html", title="Registration", form=form,
                           current_user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.get_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template("form.html", title="Login", message="Wrong email or password", form=form,
                               current_user=current_user)
    return render_template("form.html", title="Login", form=form,
                           current_user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/profile/<section>")
@login_required
def profile(section):
    if current_user.is_admin:
        return redirect("/admin")
    if section == "settings":
        return render_template("settings.html", title="Settings", current_user=current_user)
    if section == "sites":
        db_sess = db_session.get_session()
        sites = list(db_sess.query(Site).filter(Site.user_id == current_user.id))
        return render_template("sites.html", title="Sites", current_user=current_user, sites=sites)
    if section == "organizations":
        db_sess = db_session.get_session()
        organizations = list(db_sess.query(Organization).filter(Organization.user_id == current_user.id))
        return render_template("organizations.html", title="Organizations", current_user=current_user,
                               organizations=organizations)


@app.route("/profile/sites/add", methods=["GET", "POST"])
@login_required
def add_site():
    if current_user.is_admin:
        return redirect("/admin")
    form = AddSiteForm()
    if form.validate_on_submit():
        db_sess = db_session.get_session()
        if len(list(db_sess.query(Site).filter(Site.name == form.name.data))) != 0:
            return render_template("sites_add.html", title="Add site", current_user=current_user, form=form,
                                   message="This site name is already using")
        if len(list(db_sess.query(Site).filter(Site.url == form.url.data))) != 0:
            return render_template("sites_add.html", title="Add site", current_user=current_user, form=form,
                                   message="This URL is already using")
        site = Site(
            key=random_key_gen(),
            name=form.name.data,
            url=form.url.data,
            user=current_user
        )
        db_sess.add(site)
        db_sess.commit()
        return redirect("/profile/sites")
    return render_template("sites_add.html", title="Add site", current_user=current_user, form=form)


@app.route("/profile/sites/<site_name>")
@login_required
def site_info(site_name):
    if current_user.is_admin:
        return redirect("/admin")
    db_sess = db_session.get_session()
    site = db_sess.query(Site).filter(Site.name == site_name).first()
    if site.user_id != current_user.id:
        return
    views_per_day = len(list(db_sess.query(PromoView).filter(PromoView.site_id == site.id,
                                                        PromoView.date >= datetime.now() - timedelta(days=1))))
    return render_template("site_info.html", site=site, views_per_day=views_per_day, title="Site info",
                           current_user=current_user)


@app.route("/profile/organizations/add", methods=["GET", "POST"])
@login_required
def add_organization():
    if current_user.is_admin:
        return redirect("/admin")
    form = AddOrganizationForm()
    if form.validate_on_submit():
        db_sess = db_session.get_session()
        if len(list(db_sess.query(Organization).filter(Organization.name == form.name.data))) != 0:
            return render_template("organizations_add.html", title="Add organization", current_user=current_user,
                                   form=form,
                                   message="This organization name is already using")
        if len(list(db_sess.query(Organization).filter(Organization.url == form.url.data))) != 0:
            return render_template("organizations_add.html", title="Add organization", current_user=current_user,
                                   form=form,
                                   message="This URL is already using")
        organization = Organization(
            name=form.name.data,
            url=form.url.data,
            user=current_user
        )
        db_sess.add(organization)
        db_sess.commit()
        return redirect("/profile/organizations")
    return render_template("organizations_add.html", title="Add organization", current_user=current_user, form=form)


@app.route("/profile/organizations/<organization_name>")
@login_required
def organization_info(organization_name):
    if current_user.is_admin:
        return redirect("/admin")
    return redirect(f"/profile/organizations/{organization_name}/promos/not_verified")


@app.route("/profile/organizations/<organization_name>/promos/not_verified")
@login_required
def promos_not_verified(organization_name):
    if current_user.is_admin:
        return redirect("/admin")
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.name == organization_name).first()
    if organization.user_id != current_user.id:
        return
    promos = db_sess.query(Promo).filter(Promo.organization_id == organization.id, Promo.verified == False)[::-1]
    return render_template("promos_not_verified.html", title="Not verified promos", current_user=current_user,
                           promos=promos, organization=organization)


@app.route("/profile/organizations/<organization_name>/promos/verified")
@login_required
def promos_verified(organization_name):
    if current_user.is_admin:
        return redirect("/admin")
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.name == organization_name).first()
    if organization.user_id != current_user.id:
        return
    promos = db_sess.query(Promo).filter(Promo.organization_id == organization.id, Promo.verified == True,
                                         Promo.published == False)[::-1]
    return render_template("promos_verified.html", title="Verified promos", current_user=current_user,
                           promos=promos, organization=organization, last_cost=last_cost,
                           organization_name=organization_name)


@app.route("/profile/organizations/<organization_name>/promos/add", methods=["GET", "POST"])
@login_required
def add_promos(organization_name):
    if current_user.is_admin:
        return redirect("/admin")
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.name == organization_name).first()
    if organization.user_id != current_user.id:
        return
    form = AddPromoForm()
    if form.validate_on_submit():
        promo = Promo(
            header=form.header.data,
            text=form.text.data,
            cost=None,
            organization_id=organization.id,
            url=form.url.data
        )
        db_sess.add(promo)
        db_sess.commit()
        return redirect(f"/profile/organizations/{organization_name}")
    return render_template("promos_add.html", title="Add promo", current_user=current_user,
                           organization=organization, form=form)


@app.route("/profile/organizations/<organization_name>/promos/publish/<promo_id>")
@login_required
def publish_promo(organization_name, promo_id):
    if current_user.is_admin:
        return redirect("/admin")
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.name == organization_name).first()
    if organization.user_id != current_user.id:
        return
    promo = db_sess.query(Promo).filter(Promo.id == promo_id, Promo.verified == True, Promo.published == False).first()
    db_sess.delete(promo)
    promo.cost = last_cost
    promo.created_date = datetime.now()
    promo.verified = True
    promo.published = True
    db_sess.add(promo)
    db_sess.commit()
    return redirect(f"/")


@app.route("/admin")
@app.route("/admin/promos")
@login_required
def admin_promos():
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    promos = db_sess.query(Promo).filter(Promo.verified == False)[::]
    return render_template("admin_promos.html", title="Promos verifying", current_user=current_user,
                           promos=promos)


@app.route("/admin/promos/verify/<promo_id>")
@login_required
def admin_promos_verify(promo_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    promo = db_sess.query(Promo).filter(Promo.verified == False, Promo.id == promo_id).first()
    db_sess.delete(promo)
    promo.verified = True
    db_sess.add(promo)
    db_sess.commit()
    return redirect("/admin/promos")


@app.route("/admin/promos/decline/<promo_id>")
@login_required
def admin_promos_decline(promo_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    promo = db_sess.query(Promo).filter(Promo.verified == False, Promo.id == promo_id).first()
    db_sess.delete(promo)
    db_sess.commit()
    return redirect("/admin/promos")


@app.route("/admin/organizations")
@login_required
def admin_organizations():
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    organizations = db_sess.query(Organization).filter(Organization.verified == False)[::]
    return render_template("admin_organizations.html", title="Organizations verifying", current_user=current_user,
                           organizations=organizations)


@app.route("/admin/organizations/verify/<organization_id>")
@login_required
def admin_organizations_verify(organization_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.verified == False, Organization.id == organization_id).first()
    db_sess.delete(organization)
    organization.verified = True
    db_sess.add(organization)
    db_sess.commit()
    return redirect("/admin/organizations")


@app.route("/admin/organizations/decline/<organization_id>")
@login_required
def admin_organizations_decline(organization_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    organization = db_sess.query(Organization).filter(Organization.verified == False, Organization.id == organization_id).first()
    db_sess.delete(organization)
    db_sess.commit()
    return redirect("/admin/organizations")


@app.route("/admin/sites")
@login_required
def admin_sites():
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    sites = db_sess.query(Site).filter(Site.verified == False)[::]
    return render_template("admin_sites.html", title="Sites verifying", current_user=current_user,
                           sites=sites)


@app.route("/admin/sites/verify/<site_id>")
@login_required
def admin_sites_verify(site_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    site = db_sess.query(Site).filter(Site.verified == False, Site.id == site_id).first()
    db_sess.delete(site)
    site.verified = True
    db_sess.add(site)
    db_sess.commit()
    return redirect("/admin/sites")


@app.route("/admin/sites/decline/<site_id>")
@login_required
def admin_sites_decline(site_id):
    if not current_user.is_admin:
        return
    db_sess = db_session.get_session()
    site = db_sess.query(Site).filter(Site.verified == False, Site.id == site_id).first()
    db_sess.delete(site)
    db_sess.commit()
    return redirect("/admin/sites")


def cost_counter():
    global last_cost
    base_cost = 1000
    iters = 0
    db_sess = db_session.get_session()
    while True:
        promos = db_sess.query(Promo).filter(Promo.published == True, Promo.created_date >= datetime.now() - timedelta(days=3))
        current_cost = base_cost
        for promo in promos:
            b = base_cost
            c = promo.cost
            if c is None:
                c = 0
            t = math.sqrt(c + b ** 2)
            x = (datetime.now() - promo.created_date).seconds
            current_cost += round(max(0., -(x + 1) ** math.log(x + 1, t) + c + 1), 2)
        cost = Cost(
            value=current_cost
        )
        db_sess.add(cost)
        try:
            db_sess.commit()
        except Exception as err:
            print(f"{err.__class__.__name__}: err")
        last_cost = current_cost
        # if iters % 180 == 0:
        #     promo = Promo(
        #         header=f'Conpany no.{iters}',
        #         text='TRY OUR NEW COOL PRODUCT',
        #         cost=last_cost,
        #         organization_id=iters,
        #     )
        #     db_sess.add(promo)
        #     db_sess.commit()
        iters += 1
        sleep(5)


if __name__ == "__main__":
    db_session.global_init("db/main_board.db")
    db_session.create_session()
    # db_sess = db_session.get_session()
    # promo = Promo(
    #     header=f'Conpany no.{1}',
    #     text='TRY OUR NEW COOL PRODUCT',
    #     cost=1000,
    #     organization_id=1,
    # )
    # db_sess.add(promo)
    # db_sess.commit()
    thr = threading.Thread(target=cost_counter)
    thr.start()
    app.run(host="127.0.0.1", port=8080)
