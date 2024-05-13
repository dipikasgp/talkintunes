from talkintunes.config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URI = os.getenv("DATABASE_URI")
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()




def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    # app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from talkintunes.users.routes import users
    from talkintunes.messages.routes import message
    from talkintunes.main.routes import main
    from talkintunes.errors.handlers import errors

    app.register_blueprint(users)
    app.register_blueprint(message)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app