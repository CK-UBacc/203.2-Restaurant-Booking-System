from flask import Flask
from .models import database

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
    app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

    database.init_app(app)

    from .routes import view
    from .dashboardRoutes import dashboard

    app.register_blueprint(view)
    app.register_blueprint(dashboard, url_prefix="/dashboard") #

    return app