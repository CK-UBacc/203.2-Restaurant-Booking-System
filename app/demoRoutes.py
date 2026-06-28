'''
Demo route that shows a sample restaurant booking page using TableFlow.
Used to demonstrate to potential restaurant clients what the booking system looks like.
'''
from flask import Blueprint, render_template
from .models import TimeSlot, Table, RestaurantSettings
import datetime

demo = Blueprint("demo", __name__)

@demo.route("")
def indexDemo():
    '''
    Route to restaurant demo page.
    '''
    restaurant_settings = RestaurantSettings.query.first()
    return render_template('indexMain.html', restaurant_settings=restaurant_settings)

@demo.route("/example")
def exampleRestaurant():
    '''
    Shows what a restaurant booking page looks like using TableFlow.
    '''
    # Load all time slots, tables and restaurant settings needed to display the booking form
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    # Pass today's date so the date picker can block dates in the past
    today = datetime.date.today()
    restaurant_settings = RestaurantSettings.query.first()
    return render_template('indexDemo.html', timeSlots=timeSlots, tables=tables, today=today, restaurant_settings=restaurant_settings)