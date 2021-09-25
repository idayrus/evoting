from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Import
from app.helper.sqlalchemy import MyQuery
from app.helper.rproxy import ReverseProxied

# Init app
app = Flask(
    __name__,
    static_url_path = '/file/public',
    static_folder = '../file/public',
    template_folder = 'template'
)
app.config.from_object('config')

# Proxied
app.wsgi_app = ReverseProxied(app.wsgi_app, app.config)

# Main database
db_main = SQLAlchemy(query_class=MyQuery)
db_main.init_app(app)

# Database migration
migrate = Migrate(app, db_main)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user.login"

# Register middleware
from app.helper.middleware import *

# Import a module / component using its blueprint handler variable.
from app.module.report.route import report_route
from app.module.candidate.route import candidate_route
from app.module.voter.route import voter_route
from app.module.user.route import user_route
from app.module.setting.route import setting_route

# Register blueprint(s)
app.register_blueprint(report_route)
app.register_blueprint(candidate_route)
app.register_blueprint(voter_route)
app.register_blueprint(user_route)
app.register_blueprint(setting_route)

# Logger
from app.helper.logger import register_logger
register_logger(app, "app.log")
