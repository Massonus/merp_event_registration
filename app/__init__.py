import os

from dotenv import load_dotenv
from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder='../static')
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'

    from app.routes import routes
    from app.api_routes import api

    app.register_blueprint(routes)
    app.register_blueprint(api, url_prefix='/api')

    with app.app_context():
        from . import models
        db.create_all()
        create_admin()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def create_admin():
    from app.models import User
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if User.query.filter_by(email=admin_email).first() is None:
        hashed_password = generate_password_hash(admin_password)
        admin_user = User(email=admin_email, password=hashed_password, is_admin=True)
        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user {admin_email} created successfully!")
    else:
        print("Admin user already exists!")
