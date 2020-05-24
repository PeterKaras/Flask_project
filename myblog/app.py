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

from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import PasswordField
from wtforms.validators import InputRequired
from wtforms import TextAreaField

flask_app = Flask(__name__)
flask_app.config.from_pyfile("/vagrant/configs/default.py")
flask_app.config.from_pyfile("/vagrant/configs/develop.py")

if "MYBLOG_CONFIG" in os.environ:
    flask_app.config.from_envvar("MYBLOG_CONFIG")

#FORMS
class LoginForm(FlaskForm):
    username = StringField("Username", validators= [InputRequired()])
    password = StringField("Password", validators= [InputRequired()])                       

class ArticleForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired()])
    content = TextAreaField("Content")
    
# CONTROLLERS
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

#ARTICLES
@flask_app.route("/articles/",methods=["GET"])
def view_articles():
    db = get_db()
    cur = db.execute("select * from articles order by id desc")
    articles = cur.fetchall()
    return render_template("articles.jinja",articles=articles)

@flask_app.route("/article/new",methods=["GET"])
def view_add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    form = ArticleForm()
    return render_template("article_editor.jinja",form=form)

@flask_app.route("/articles/<int:art_id>/edit/",methods=["GET"])
def view_article_editor(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    edit_form = ArticleForm(request.form)
    if edit_form.validate():
        db = get_db()
        cur = db.execute("select * from articles where id=(?)",[art_id])
        article = cur.fetchone()
        if article:
            form = ArticleForm()
            form.title.data = article["title"]
            form.content.data = article["content"]
            return render_template("article_editor.jinja",form=form,article = article)
        else:
            return render_template("page_not_found.jinja")
    else:
        for error in login.form.errors:
            flash("{} is missing!".format(error),"alert-danger")
        return redirect(url_for("view_login"))

@flask_app.route("/article/<int:art_id>",methods=["POST"])
def edit_article(art_id):
    if "logged" not in session:
        return redirect(url_for("view_login"))
    
    db = get_db()
    cur = db.execute("select * from articles where id=(?)",[art_id])
    article = cur.fetchone()
    if article:
        edit_form = ArticleForm(request.form)
        if edit_form.validate():
            db.execute("update articles set title=?,content=? where id=?",
                 [edit_form.title.data,edit_form.content.data,art_id])
            db.commit()
            flash("Edit saved","alert-success")
            return redirect(url_for("view_article",art_id = art_id))
        else:
            for error in login.form.errors:
                flash("{} is missing!".format(error),"alert-danger")
            return redirect(url_for("view_login"))
    else:
        return redirect(url_for("view_article",art_id = art_id))
    
@flask_app.route("/articles/",methods=["POST"])
def add_article():
    if "logged" not in session:
        return redirect(url_for("view_login"))
    edit_form = ArticleForm(request.form)
    if edit_form.validate():
        db = get_db()
        db.execute("insert into articles (title,content) values (?,?)",
                [request.form.get("title"),request.form.get("content")])
        db.commit()
        flash("Article was saved!","alert-success")
        return redirect(url_for("view_articles"))
    else:
        for error in login.form.errors:
            flash("{} is missing!".format(error),"alert-danger")
        return redirect(url_for("view_login"))


@flask_app.route("/articles/<int:art_id>/")
def view_article(art_id):
    db = get_db()
    cur = db.execute("select * from articles where id=(?)",[art_id])
    article = cur.fetchone()                  
    if article:
        return render_template("article.jinja",article=article)
    return render_template("page_not_found.jinja",art_id=art_id)

#LOGIN AND LOGOUT
@flask_app.route("/login/", methods = ["GET"])
def view_login():
    #dostam login stranku ked nie som prihlaseny alebo som sa zadal nespravne
    #zobrazuje GET heslo a meno v url adresse co nechceme
    login_form = LoginForm()
    return render_template("login.jinja",form = login_form)

@flask_app.route("/login/", methods = ["POST"])
def view_user():
    #kontrola udajov a prvotne prihlasovanie
    login_form = LoginForm(request.form)
    if login_form.validate():#skontroluje ci vyplnit vsetko
        if login_form.username.data == flask_app.config["USERNAME"] and \
           login_form.password.data == flask_app.config["PASSWORD"]:
            session["logged"] = True
            flash("Login successful","alert-success")
            return redirect(url_for("view_admin"))
        else:
            flash("Invalid credentials","alert-danger")
            return render_template("login.jinja",form = login_form)
    else:
        for error in login.form.errors:
            flash("{} is missing!".format(error),"alert-danger")
        return redirect(url_for("view_login"))
    
@flask_app.route("/logout/",methods = ["POST"])
def logout_user():
    session.pop("logged")
    flash("Logout successful","alert-success")
    return redirect(url_for("view_welcome_page"))

#utils DATABASE
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
