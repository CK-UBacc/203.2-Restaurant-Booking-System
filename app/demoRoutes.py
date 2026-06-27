'''
Demo of our 
'''
from flask import Blueprint, render_template
from .models import TimeSlot, Table, RestaurantSettings
import datetime

demo = Blueprint("demo", __name__)

@demo.route("")
def exampleRestaurant():
    '''
    Shows what a restaurant booking page looks like using TableFlow.
    '''
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    today = datetime.date.today()
    restaurant_settings = RestaurantSettings.query.first()
    return render_template('indexDemo.html', timeSlots=timeSlots, tables=tables, today=today, restaurant_settings=restaurant_settings)