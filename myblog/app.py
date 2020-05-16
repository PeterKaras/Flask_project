from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from flask import g
from flask import flash
import os
import sqlite3

flask_app = Flask(__name__)
flask_app.config.from_pyfile("/vagrant/configs/default.py")
flask_app.config.from_pyfile("/vagrant/configs/develop.py")

if "MYBLOG_CONFIG" in os.environ:
    flask_app.config.from_envvar("MYBLOG_CONFIG")

@flask_app.route("/")
def view_welcome_page():
    return render_template("welcome_page.jinja")

@flask_app.route("/about/")
def view_about():
    return render_template("about.jinja")

@flask_app.route("/admin/")
def view_admin():
    if "logged" not in session:
        flash("You must be logged in","alert-danger")
        return redirect(url_for("view_login"))
    return render_template("admin.jinja")

@flask_app.route("/articles/",methods=["GET"])
def view_articles():
    db = get_db()
    cur = db.execute("select * from articles order by id desc")
    articles = cur.fetchall()
    return render_template("articles.jinja",articles=articles)

@flask_app.route("/articles/",methods=["POST"])
def add_article():
    db = get_db()
    db.execute("insert into articles (title,content) values (?,?)",
                [request.form.get("title"),request.form.get("content")])
    db.commit()
    flash("Article was saved!","alert-success")
    return redirect(url_for("view_articles"))

@flask_app.route("/articles/<int:art_id>/")
def view_article(art_id):
    db = get_db()
    cur = db.execute("select * from articles where id=(?)",[art_id])
    article = cur.fetchone()                  
    if article:
        return render_template("article.jinja",article=article)
    return render_template("page_not_found.jinja",art_id=art_id)

@flask_app.route("/login/", methods = ["GET"])
def view_login():
    #dostam login stranku ked nie som prihlaseny alebo som sa zadal nespravne
    #zobrazuje GET heslo a meno v url adresse co nechceme
    return render_template("login.jinja")

@flask_app.route("/login/", methods = ["POST"])
def view_user():
    #kontrola udajov a prvotne prihlasovanie
    username = request.form["username"]
    password = request.form["password"]
    if username == flask_app.config["USERNAME"] and \
       password == flask_app.config["PASSWORD"]:
        session["logged"] = True
        flash("Login successful","alert-success")
        return redirect(url_for("view_admin"))
    else:
        flash("Invalid credentials","alert-danger")
        return redirect(url_for("view_login"))
    
@flask_app.route("/logout/",methods = ["POST"])
def logout_user():
    session.pop("logged")
    flash("Logout successful","alert-success")
    return redirect(url_for("view_welcome_page"))

#utils
def connect_db():
    #pripajam sa na databazu
    rv = sqlite3.connect(flask_app.config["DATABASE"])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    #dostavam databazu
    if not hasattr(g, "sqlite_db"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@flask_app.teardown_appcontext
def close_db(error):
    #error je povinna hodnota a zatvaranie databazy
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

def init_db(app):
    #bude inicializovat databasu
    with app.app_context():
        db = get_db()
        with open("myblog/schema.sql","r") as fp:
            db.cursor().executescript(fp.read())
        db.commit()

#192.168.1.19
