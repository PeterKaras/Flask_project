from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Article(db.Model):
    id = db.Column(db.Intiger, primary_key = True)
    title = db.Column(db.String)
    content = db.Column(db.String)
