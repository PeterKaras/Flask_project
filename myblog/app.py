from flask import Flask
from flask import render_template

flask_app= Flask(__name__)

@flask_app.route("/")
def view_main():
    return render_template("_main.jinja")

@flask_app.route("/about/")
def view_about():
    return render_template("about.jinja")

@flask_app.route("/welcome_page")
def view_welcome():
    return "This is main page!"

@flask_app.route("/admin/")
def view_admin():
    return "U have logged in"

@flask_app.route("/articles/")
def view_articles():
    return "Here should be some articles!"
#192.168.1.19
