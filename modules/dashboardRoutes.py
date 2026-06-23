from flask import Blueprint, render_template, redirect, url_for, request
from .models import Table, Booking, TimeSlot
import datetime

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/", methods=["GET"])
def dashboardIndex():
    '''
    Route to dashboard
    Dashboard is supposed to display the restaurants data and act as the hub page for a restaurant manager

    Args:

    Returns:
    render_template: template for the dashboard with all of the data for it.
    '''

    bookings = Booking.query.all()
    tables = Table.query.all()
    return render_template("dashboardOverview.html", bookings=bookings, tables=tables, active="overview")

@dashboard.route("/bookings", methods=["GET"])
def dashboardBookings():
    '''
    Route to the manage bookings page of the dashboard.

    Args:
    None

    Returns:
    render_template: template for the manage bookings page with all bookings.
    '''
    bookings = Booking.query.all()
    return render_template("dashboardBookings.html", bookings=bookings, active="bookings")

@dashboard.route("/tables", methods=["GET"])
def dashboardTables():
    '''
    Route to the manage tables page of the dashboard.

    Args:
    None

    Returns:
    render_template: template for the manage tables page with all tables.
    '''
    tables = Table.query.all()
    return render_template("dashboardTables.html", tables=tables, active="tables")
