'''
Routes for common errors.
Registers custom error pages for 404 and 500 HTTP errors.
Note: these handlers are registered on the blueprint so they only catch errors that occur within this blueprint.
To catch errors across the whole app they would need to be registered on the app object using @app.errorhandler instead.
'''
from flask import Blueprint, render_template
from .models import database # I don't know if this will not allow the database to be changed but it stops the error popups

errorRoute = Blueprint("error", __name__)

# Shown when the user tries to visit a URL that does not exist
@errorRoute.errorhandler(404)
def notFound(error):
    return render_template("error.html", code=404, message="Page not found."), 404

# Shown when an unhandled exception occurs on the server
# Rolls back the database session first so any failed transaction does not leave the database in a broken state
@errorRoute.errorhandler(500)
def internalError(error):
    database.session.rollback()
    return render_template("error.html", code=500, message="Internal server error"), 500
