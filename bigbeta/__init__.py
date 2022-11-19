"""
Init file

To recreate the SQLite database with new columns
    Create a backup of db file
    mv ~/bigbeta/bigbeta/site.db ~/bigbeta/bigbeta/bkup_<dt>_site.db
    run ipython from top level dir
    from bigbeta import create_app
    app = create_app()
    app.app_context().push()
    from bigbeta import db
    db.create_all()

    How do I move data from old db to new quickly?
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from bigbeta.config import Config


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()


def create_app(config_class=Config):
    """
    Creates app
    """

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from bigbeta.users.routes import users
    from bigbeta.posts.routes import posts
    from bigbeta.sends.routes import sends
    from bigbeta.main.routes import main
    from bigbeta.stocks.routes import stocks
    from bigbeta.errors.handlers import errors
    from bigbeta.visualizations.routes import visualizations
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(sends)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(visualizations)
    app.register_blueprint(stocks)

    return app


def create_app_context(confif_class=Config):
    """
    Creates app context for use by cron jobs or other external services.
        Using the above create_app function will result in circular import errors
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    return app
