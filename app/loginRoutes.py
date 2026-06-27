from flask import Blueprint, request, render_template, render_template, redirect, url_for, session
from .models import User

login = Blueprint("login", __name__)

@login.route("/loginpage", methods=["GET","POST"])
def loginpage(): # This function name case is fucked but changin it will be a headache
    if request.method == "POST":

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
       
    return render_template("loginpage.html")

@login.route("/Logout")
def logout():
    session.clear

    return redirect(url_for("login.loginpage"))