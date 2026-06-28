'''
Constructs the flask object to return to "run.py"
'''

from flask import Flask
from .models import database, RestaurantSettings
from .bookingRoutes import mail

def create_app():
    '''
    Function that constructs the flask application

    :return Flask: The flask application object
    '''
    app = Flask(__name__)
    app.config.from_object("config")
    
    # Remember me feature
    # Not sure if this is supposed to be here or somewhere else
    from datetime import timedelta #Sets remember me time duration to 30 days
    app.permanent_session_lifetime = timedelta(days=30) #Tells flask how long a single session can be live for


    # Bind the database and mail extensions to this app instance
    database.init_app(app)
    mail.init_app(app)

    '''
    @app.context_processor
    def inject_settings():
        try:
            settings = RestaurantSettings.query.first()
        except Exception:
            settings = None
        return dict(restaurant_settings=settings)
    '''
    # Import routes into app
    # I hate how incosistent these names are but it is the quickest way of doing things without rewriting more of the app than I wan't to
    from .loginRoutes import login
    from .dashboardRoutes import dashboard
    from .bookingRoutes import bookingRoute
    from .routes import view
    from .errorRoutes import errorRoute
    from .demoRoutes import demo

    # Register each blueprint with the app
    # dashboard and demo use a url_prefix so all their routes start with /dashboard and /demo respectively
    app.register_blueprint(login)
    app.register_blueprint(dashboard, url_prefix="/dashboard")
    app.register_blueprint(bookingRoute)
    app.register_blueprint(view)
    app.register_blueprint(errorRoute)
    app.register_blueprint(demo, url_prefix="/demo")

    return app