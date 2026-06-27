'''

'''
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from .models import RestaurantSettings, Booking, Table
from sqlalchemy import func
import datetime

view = Blueprint("view", __name__)

@view.route("/")
def index():
    '''Route to home page.

    There is currently no home page but the most important page for admins to access is the login page

    :return render_template: template for the home page
    '''
    #return redirect(url_for("dashboard"))
    return redirect(url_for("login.loginpage"))

@view.route("/api/availability")
def apiAvailability():
    '''Retuns table availability.

    API returns JSON data for frontend use.

    Important for booking form table booking.
    '''
    date_str = request.args.get("date")
    time_str = request.args.get("time")

    if not date_str or not time_str:
        return jsonify({"error": "Missing date or time"}), 400

    try:
        date = datetime.date.fromisoformat(date_str)
        time = datetime.time.fromisoformat(time_str)
    except ValueError:
        return jsonify({"error": "Invalid date or time format"}), 400

    # Find all bookings at this excact date
    occupied_bookings = Booking.query.filter(
        Booking.date == date,
        Booking.time == time,
        func.upper(Booking.status).in_(["PENDING", "APPROVED"])
    ).all()

    # Collect table ID thar are occupied
    occupied_ids = set()
    for booking in occupied_bookings:
        for table in booking.tables:
            occupied_ids.add(table.id)

    tables = Table.query.all()
    result = [
        {
            "id": t.id,
            "seats": t.seats,
            "status": "OCCUPIED" if t.id in occupied_ids else "AVAILABLE"
        }
        for t in tables
    ]

    available_count = sum(1 for t in result if t["status"] == "AVAILABLE")

    return jsonify({"tables": result, "available_count": available_count, "date": date_str, "time": time_str})