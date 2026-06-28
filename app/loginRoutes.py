'''
Routes for admin login and logout.
Handles session creation when credentials are correct and session removal on logout.
'''
from flask import Blueprint, request, render_template, redirect, url_for, session
from .models import User

login = Blueprint("login", __name__)

@login.route("/loginpage", methods=["GET","POST"])
def loginpage(): # This function name case is fucked but changin it will be a headache
    # GET request shows the empty login form
    # POST request reads submitted credentials and checks them against the database
    if request.method == "POST":

        # Read the username and password submitted from the login form
        username = request.form.get("AdminUsername")
        password = request.form.get("Adminpassword")

        # Check if the remember me checkbox was ticked by the user
        remember_me = request.form.get("remember_me") == "on"

        # Search the database for a user record matching the entered username and password
        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            # Store login state and username in the session so other routes can check it
            session["logged_in"] = True
            session["username"] = user.username

            # If remember me is on the session will survive after the browser is closed
            session.permanent = remember_me

            return redirect(url_for("dashboard.dashboardIndex"))

        # No matching user found so show the login page again with an error message
        return render_template("loginpage.html",
                               error="Incorrect Username Or Password"
            )

    # Default GET request just shows the login form with no error
    return render_template("loginpage.html")

@login.route("/Logout")
def logout():
    # Remove all session data so the user is no longer considered logged in
    session.clear()

    return redirect(url_for("login.loginpage"))