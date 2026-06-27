'''
Routes for common errors
'''
from flask import Blueprint, render_template
from .models import database # I don't know if this will not allow the database to be changed but it stops the error popups

errorRoute = Blueprint("error", __name__)

@errorRoute.errorhandler(404)
def notFound(error):
    return render_template("error.html", code=404, message="Page not found."), 404

@errorRoute.errorhandler(500)
def internalError(error):
    database.session.rollback()
    return render_template("error.html", code=500, message="Internal server error"), 500
