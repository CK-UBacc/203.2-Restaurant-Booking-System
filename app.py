from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
# import os # not currently being used?
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

database = SQLAlchemy(app)

#-------------------------------------------------------------------------------------------------------
# Database tables stuff
#
# Don't know how this could be used to create different tables for different restaurants. I'll figure it out
#-------------------------------------------------------------------------------------------------------
class Table(database.Model): 
    __tablename__ = "tables"

    id = database.Column(database.Integer, primary_key=True)
    seats = database.Column(database.Integer)

    def __repr__(self):
        return f"{self.id}: {self.seats}"


class Booking(database.Model):
    __tablename__ = "bookings"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(128), nullable=False)
    guestCount = database.Column(database.Integer, default=1)
    phone = database.Column(database.String(32))
    email = database.Column(database.String(128))
    # Table ID and stuff goes here. Problem is that there could be multiple tables booked and also how do I do foreign keys in SQLAlchemy.
    date = database.Column(database.Date, nullable=False)
    time = database.Column(database.Time, nullable=False)
    status = database.Column(database.String(16), nullable=False)

    def __repr__(self): # I don't know how to set up the __repr__
        return f"{self.id}: {self.name}"
    
class TimeSlot(database.Model): # 
    __tablename__ = "timeSlots"

    slot = database.Column(database.Time, primary_key=True)

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

        dummyBookings = [
            Booking(
                name="Jimmy Johnson",
                guestCount=5,
                phone="2798833",
                email="email@email.email.email",
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                status="PENDING"),
            Booking(
                name="Jamie Jackson",
                guestCount=3,
                phone="0404040",
                email="dummy@email.email.email",
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                status="EXPIRED"),
            Booking(
                name="Jackie Chan",
                guestCount=2,
                phone="8456215",
                email="Thebest@email.email.email",
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                status="APPROVED"),
            Booking(
                name="Your mum",
                guestCount=5,
                phone="4567892",
                email="fatass@email.email.email",
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                status="CANCELED")
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
                status="Pending")

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
    timeSlots = TimeSlot.query.all()
    return render_template("dashboardBookings.html", bookings=bookings, timeSlots=timeSlots, active="bookings")

@app.route("/dashboard/bookings/add", methods=["POST"]) #    Create a new booking record in the database

def dashboardBookingsAdd(): #    New bookings are show "Pending" status by default


    try:
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        guestCount = int(request.form.get("guestCount"))
        date = datetime.date.fromisoformat(request.form.get("date"))
        time = datetime.datetime.strptime(request.form.get("time"), "%H:%M:%S").time()

        newBooking = Booking(
            name=name,
            guestCount=guestCount,
            email=email,
            phone=phone,
            date=date,
            time=time,
            status="Pending")

        database.session.add(newBooking)
        database.session.commit()
        flash("Booking added successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to add booking. Please check all fields.", "error")

    return redirect(url_for("dashboardBookings"))

@app.route("/dashboard/bookings/edit/<int:id>", methods=["POST"])  #Updates all fields of an exist booking (name, email, phone, guest count,date, time, and status)

def dashboardBookingsEdit(id):

    try:
        booking = Booking.query.get_or_404(id)
        booking.name = request.form.get("name")
        booking.email = request.form.get("email")
        booking.phone = request.form.get("phone")
        booking.guestCount = int(request.form.get("guestCount"))
        booking.date = datetime.date.fromisoformat(request.form.get("date"))
        booking.time = datetime.datetime.strptime(request.form.get("time"), "%H:%M:%S").time()
        booking.status = request.form.get("status")
        database.session.commit()
        flash("Booking updated successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to update booking.", "error")
    return redirect(url_for("dashboardBookings"))

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

@app.route("/dashboard/tables/add", methods=["POST"])  # Creates a new table record with the specific seat count
def dashboardTablesAdd():
    
    try:
        seats = int(request.form.get("seats"))
        database.session.add(Table(seats=seats))
        database.session.commit()
        flash("Table added successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to add table.", "error")
    return redirect(url_for("dashboardTables"))

@app.route("/dashboard/tables/edit/<int:id>", methods=["POST"]) # Updates the seat number in existing table
def dashboardTablesEdit(id):

    try:
        table = Table.query.get_or_404(id)
        table.seats = int(request.form.get("seats"))
        database.session.commit()
        flash("Table updated successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to update table.", "error")
    return redirect(url_for("dashboardTables"))

@app.route("/dashboard/tables/delete/<int:id>", methods=["POST"]) # Delete a table
def dashboardTablesDelete(id):

    try:
        table = Table.query.get_or_404(id)
        database.session.delete(table)
        database.session.commit()
        flash("Table deleted.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to delete table.", "error")
    return redirect(url_for("dashboardTables"))

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
                           timeSlots=timeSlots
                           )

# Admin Account for Loginpage
ADMIN_USERNAME = "admin123" #Username is admin123
ADMIN_PASSWORD = "admin123" #Password is admin123

@app.route("/loginpage", methods=["GET","POST"])
def loginpage():
    

    if request.method == "POST":
        username = request.form.get("AdminUsername")
        password = request.form.get("Adminpassword")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("loginpage.html")

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