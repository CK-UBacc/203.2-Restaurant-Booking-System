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
        try:
            username = request.form.get("AdminUsername")
            password = request.form.get("Adminpassword")

            remember_me = request.form.get("remember_me") == "on"

            user = User.query.filter_by(
                username=username,
                password=password
            ).first()

            if user:
                session["logged_in"] = True
                session["username"] = user.username

                session.permanent = remember_me

                return redirect(url_for("dashboard.dashboardIndex"))
            
            return render_template("loginpage.html",
                                   error="Incorrect Username Or Password"
                )
        
        except Exception as e:
            return render_template("loginpage.html",
                                   error=f"An error has occured: {e}"
                )
            
    return render_template("loginpage.html")

@login.route("/Logout")
def logout():
    # Remove all session data so the user is no longer considered logged in
    session.clear()

    return redirect(url_for("login.loginpage"))