from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    app.secret_key = os.getenv("SECRET_KEY", None)

    db.init_app(app)
    Migrate(app, db)

    return app

app = create_app()
