from flask import Flask, render_template, redirect, url_for, request
#from flask_sqlalchemy import SQLAlchemy # moved to models.py
# import os # not currently being used?
import datetime

from modules.models import database
from tests.dummyDatabase import * # Importing the dummy data and debug funcitons remove in final product



#from wtformsTesting import * # Not used

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

# Connects the database created in models.py to app created here.
database.init_app(app)
 

from modules.routes import *
#-------------------------------------------------------------------------------------------------------
# Database tables stuff
#
# Don't know how this could be used to create different tables for different restaurants. I'll figure it out
#-------------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------------
# Routes
#-------------------------------------------------------------------------------------------------------

#-------------------------------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    initializeDummyDatabase(app, database)
    
    app.run(debug=True)