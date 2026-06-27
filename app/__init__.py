'''
Constructs the flask object to return to "run.py"
'''

from flask import Flask
from .models import database
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


    # Import database into app
    database.init_app(app)
    mail.init_app(app)

    # Import routes into app
    from .loginRoutes import login
    from .dashboardRoutes import dashboard

    app.register_blueprint(login)
    app.register_blueprint(dashboard, url_prefix="/dashboard") #

    return app