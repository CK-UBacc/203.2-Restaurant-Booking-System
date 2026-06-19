from flask import Flask, render_template, redirect, url_for, request
#from flask_sqlalchemy import SQLAlchemy # moved to models.py
# import os # not currently being used?
import datetime

from modules.models import *


#from wtformsTesting import * # Not used

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

# database = SQLAlchemy(app)

# Connects the database created in models.py to app created here.
database.init_app(app)
 

#-------------------------------------------------------------------------------------------------------
# Database tables stuff
#
# Don't know how this could be used to create different tables for different restaurants. I'll figure it out
#-------------------------------------------------------------------------------------------------------
def initializeDummyDatabase(): # Crate dummy database file with dummy data in tables
    '''
    Creates a dummy database for testing

    Args:
    None

    Returns:
    None
    '''
    with app.app_context():
        print("DROPPING EXISTING DUMMY DATA")
        database.drop_all()
        print("CREATING NEW DUMMY DATA TABLES")
        database.create_all()

        dummyTables = [
            Table(seats=2),
            Table(seats=4),
            Table(seats=5),
            Table(seats=4),
            Table(seats=8),
            Table(seats=4),
            Table(seats=2)
        ]

        dummyTimeSlots = [
            TimeSlot(slot = datetime.time(10,30)),
            TimeSlot(slot = datetime.time(11,)),
            TimeSlot(slot = datetime.time(11,30)),
            TimeSlot(slot = datetime.time(12)),
            TimeSlot(slot = datetime.time(12,30)),
            TimeSlot(slot = datetime.time(13)),
            TimeSlot(slot = datetime.time(13,30)),
            TimeSlot(slot = datetime.time(14)),
            TimeSlot(slot = datetime.time(14,30))
        ]

        dummyBookings = [
            Booking(
                name="Jimmy Johnson",
                guestCount=5,
                phone="2798833",
                email="email@email.email.email",
                date=datetime.date.today(),
                time=dummyTimeSlots[1].slot,
                table=1,
                status="PENDING"),
            Booking(
                name="Jamie Jackson",
                guestCount=3,
                phone="0404040",
                email="dummy@email.email.email",
                date=datetime.date.today(),
                time=dummyTimeSlots[3].slot,
                table=12,
                status="EXPIRED"),
            Booking(
                name="Jackie Chan",
                guestCount=2,
                phone="8456215",
                email="Thebest@email.email.email",
                date=datetime.date.today(),
                time=dummyTimeSlots[6].slot,
                table=4,
                status="APPROVED"),
            Booking(
                name="Your mum",
                guestCount=5,
                phone="4567892",
                email="fatass@email.email.email",
                date=datetime.date.today(),
                time=dummyTimeSlots[2].slot,
                status="CANCELED")
        ]
    
        print("INSERTING DUMMY TABLES")
        for table in dummyTables:
            database.session.add(table)
        print("INSERTING DUMMY BOOKINGS")
        for booking in dummyBookings:
            database.session.add(booking)
        print("INSERTING TIME SLOTS")
        for timeSlot in dummyTimeSlots:
            database.session.add(timeSlot)

        print("COMMITING TABLE CHANGES")
        database.session.commit()
    
        print("DUMMY DATABASE INITIALIATION COMPLETE")

#-------------------------------------------------------------------------------------------------------
# Routes
#-------------------------------------------------------------------------------------------------------
@app.route("/") #NEEDS: HTML page, Code?
def index():
    '''
    Route to home page.

    Args:
    None

    Returns:
    render_template: template for the home page
    '''
    #return render_template('index.html')
    return redirect(url_for("dashboard"))

@app.route("/booking", methods=["GET", "POST"]) #NEEDS: HTML page, Code
def booking():
    '''
    Route to booking form.
    Booking form is ment to be an embed on a page of another website so there will be no route to the booking form from our web page.

    Args:
    id (int): restaurant ID

    Returns:
    render_template: template for the booking form with data for the page
    '''
    #if request.method == "GET": # Is it even neccesary to do the get query?

    if request.method == "POST":
        try:
            name = request.form.get("name")
            print(f"\tName recieved: {name}")
            email = request.form.get("email")
            print(f"\tEmail recieved: {email}")
            phone = request.form.get("phone")
            print(f"\tPhone No. recieved: {phone}")
            guestCount = int(request.form.get("guestCount"))
            print(f"\tReservation size recieved: {guestCount}")

            date = datetime.date.fromisoformat(request.form.get("date"))
            print(f"\tDate recieved: {date}")
            time = datetime.time.strptime(request.form.get("time"), "%H:%M:%S")
            print(f"\tTime recieved: {time}")

            newBooking = Booking(
                name=name,
                guestCount=guestCount,
                email=email,
                phone=phone,
                date=date,
                time=time,
                status="PENDING")

            with app.app_context():
                database.session.add(newBooking)
                database.session.commit()

        except Exception as e:
            print(f"ERROR! {str(e)}")
    
    # Getting all the data to display on the page
    timeSlots = TimeSlot.query.all()

    return render_template("booking.html", timeSlots=timeSlots) #I don't know if the id will be needed but whatever.

@app.route("/dashboard", methods=["GET"]) #NEEDS: HTML pass, code  # ID may not be needed in the URL
def dashboard():
    '''
    Route to dashboard
    Dashboard is supposed to display the restaurants data and act as the hub page for a restaurant manager

    Args:
    id (int): The ID of the restaurant that is being managed

    Returns:
    render_template: template for the dashboard with all of the data for it.
    '''

    bookings = Booking.query.all()
    tables = Table.query.all()
    return render_template("dashboardOverview.html", bookings=bookings, tables=tables, active="overview")

@app.route("/dashboard/bookings", methods=["GET"])
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

@app.route("/dashboard/tables", methods=["GET"])
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

@app.route("/dummyData", methods=["GET"])
def dummyData():
    '''
    Just refreshing my knowledge on how to send data to an HTML page in flask

    Args:
    None

    Returns:
    render_template: the dummy template with the data
    '''
    tables = Table.query.all()
    bookings = Booking.query.all()
    timeSlots = TimeSlot.query.all()

    return render_template("dummyDataDisplay.html", 
                           tables=tables, 
                           bookings=bookings,
                           timeSlots=timeSlots,
                           )

@app.route("/updateDummyTables", methods=["POST"]) # NEEDS Data validation pass
def dummyTablesUpdate():
    '''
    Adds or edits a table based on input from page

    Args:
    None

    Returns:
    redirect: Redirects to dummy data page
    '''
    if request.method == "POST":
        try:
            table = int(request.form.get("selectedTable"))
            seats = int(request.form.get("seatsInput"))
            print(f"\tGot table no: {table}\n\tSeats: {seats}")

            
            if table == -1:
                newTable = Table(seats = seats)
                database.session.add(newTable)
            else:
                table = Table.query.get_or_404(table)
                table.seats = seats

            database.session.commit()
        except Exception as e:
            print(f"ERROR! {str(e)}")

    return redirect(url_for("dummyData"))

#-------------------------------------------------------------------------------------------------------
# Error Handling
#-------------------------------------------------------------------------------------------------------
@app.errorhandler(404) # HTML page needs to be done
def notFound(error):
    return render_template("error.html", code=404, message="Page not found."), 404

@app.errorhandler(500) # HTML page needs to be done
def internalError(error):
    database.session.rollback()
    return render_template("error.html", code=500, message="Internal server error"), 500

# For some reason the web page was trying to automaticaly get an icon that didn't exist. 
# Didn't cause any crashes or problems but it was cluttering up the terminal so this stops that.
# Remove this when we get an icon
@app.route("/favicon.ico") 
def favicon():
    return "", 204

#-------------------------------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    initializeDummyDatabase()

    app.run(debug=True)