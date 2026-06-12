from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
import os
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

database = SQLAlchemy(app)

#-------------------------------------------------------------------------------------------------------
# Database tables stuff
#
# Don't know if this could be used to create different tables for different restaurants. I'll figure it out
#-------------------------------------------------------------------------------------------------------
class Tables(database.Model): 
    __tablename__ = "tables"

    id = database.Column(database.Integer, primary_key=True)
    seats = database.Column(database.Integer)

    def __repr__(self):
        return f"{self.id}: {self.seats}"


class Bookings(database.Model):
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
            Tables(seats=2),
            Tables(seats=4),
            Tables(seats=5),
            Tables(seats=4),
            Tables(seats=8),
            Tables(seats=4),
            Tables(seats=2)
        ]

        dummyBookings = [
            Bookings(
                name="Jimmy Johnson",
                guestCount=5,
                phone="2798833",
                email="email@email.email.email",
                date=datetime.date.today(),
                time=datetime.datetime.now().time(),
                status="PENDING"),
            Bookings(
                name="Jamie Jackson",
                guestCount=3,
                phone="0404040",
                email="dummy@email.email.email",
                date=datetime.datetime.now().date(),
                time=datetime.datetime.now().time(),
                status="EXPIRED"),
            Bookings(
                name="Jackie Chan",
                guestCount=2,
                phone="8456215",
                email="Thebest@email.email.email",
                date=datetime.datetime.now().date(),
                time=datetime.datetime.now().time(),
                status="APPROVED"),
            Bookings(
                name="Your mum",
                guestCount=5,
                phone="4567892",
                email="fatass@email.email.email",
                date=datetime.datetime.now().date(),
                time=datetime.datetime.now().time(),
                status="CANCELED")
        ]
    
        print("INSERTING DUMMY TABLES")
        for table in dummyTables:
            database.session.add(table)
        print("INSERTING DUMMY BOOKINGS")
        for booking in dummyBookings:
            database.session.add(booking)

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
    return render_template('index.html')

@app.route("/booking/<int:id>", methods=["GET", "POST"]) #NEEDS: HTML page, Code
def booking(id):
    '''
    Route to booking form.
    Booking form is ment to be an embed on a page of another website so there will be no route to the booking form from our web page.

    Args:
    id (int): restaurant ID

    Returns:
    render_template: template for the booking form
    '''
    return render_template("booking.html", id=id) #I don't know if all of this will be needed but whatever.

@app.route("/dashboard/<int:id>", methods=["GET"]) #NEEDS: HTML pass, code  # ID may not be needed in the URL
def dashboard(id):
    '''
    Route to dashboard
    Dashboard is supposed to display the restaurants data and act as the hub page for a restaurant manager

    Args:
    id (int): The ID of the restaurant that is being managed

    Returns:
    render_template: template for the dashboard with all of the data for it.
    '''
    return render_template("dashboardBase.html", id=id, active="overview")

@app.route("/dashboard/<int:id>/bookings", methods=["GET"])
def manage_bookings(id):
    '''
    Route to the manage bookings page where an admin can view all bookings
    and confirm or cancel them.

    Args:
    id (int): The ID of the restaurant that is being managed

    Returns:
    render_template: template for the manage bookings page
    '''
    bookings = Bookings.query.order_by(Bookings.date.desc(), Bookings.time.desc()).all()
    return render_template("manageBookings.html", id=id, active="bookings", bookings=bookings)

@app.route("/dashboard/<int:id>/bookings/<int:booking_id>/confirm", methods=["POST"])
def confirm_booking(id, booking_id):
    '''
    Marks a booking as approved.

    Args:
    id (int): The ID of the restaurant that is being managed
    booking_id (int): The ID of the booking to confirm

    Returns:
    redirect: back to the manage bookings page
    '''
    booking = Bookings.query.get_or_404(booking_id)
    booking.status = "APPROVED"
    database.session.commit()
    flash("Booking confirmed.", "success")
    return redirect(url_for("manage_bookings", id=id))

@app.route("/dashboard/<int:id>/bookings/<int:booking_id>/cancel", methods=["POST"])
def cancel_booking(id, booking_id):
    '''
    Marks a booking as canceled.

    Args:
    id (int): The ID of the restaurant that is being managed
    booking_id (int): The ID of the booking to cancel

    Returns:
    redirect: back to the manage bookings page
    '''
    booking = Bookings.query.get_or_404(booking_id)
    booking.status = "CANCELED"
    database.session.commit()
    flash("Booking canceled.", "success")
    return redirect(url_for("manage_bookings", id=id))

@app.route("/dashboard/<int:id>/tables", methods=["GET"])
def manage_tables(id):
    '''
    Route to the manage tables page where an admin can view, add and
    remove tables.

    Args:
    id (int): The ID of the restaurant that is being managed

    Returns:
    render_template: template for the manage tables page
    '''
    tables = Tables.query.order_by(Tables.id).all()
    return render_template("manageTables.html", id=id, active="tables", tables=tables)

@app.route("/dashboard/<int:id>/tables/add", methods=["POST"])
def add_table(id):
    '''
    Adds a new table with the submitted seat count.

    Args:
    id (int): The ID of the restaurant that is being managed

    Returns:
    redirect: back to the manage tables page
    '''
    seats = request.form.get("seats", type=int)
    if seats and seats > 0:
        database.session.add(Tables(seats=seats))
        database.session.commit()
        flash("Table added.", "success")
    else:
        flash("Please enter a valid number of seats.", "error")
    return redirect(url_for("manage_tables", id=id))

@app.route("/dashboard/<int:id>/tables/<int:table_id>/delete", methods=["POST"])
def delete_table(id, table_id):
    '''
    Removes a table.

    Args:
    id (int): The ID of the restaurant that is being managed
    table_id (int): The ID of the table to delete

    Returns:
    redirect: back to the manage tables page
    '''
    table = Tables.query.get_or_404(table_id)
    database.session.delete(table)
    database.session.commit()
    flash("Table removed.", "success")
    return redirect(url_for("manage_tables", id=id))

@app.route("/dummyData")
def dummyData():
    '''
    Just refreshing my knowledge on how to send data to an HTML page in flask

    Args:
    None

    Returns:
    render_template: the dummy template with the data
    '''
    tables = Tables.query.all()
    bookings = Bookings.query.all()
    return render_template("dummyDataDisplay.html", tables=tables, bookings=bookings)

if __name__ == "__main__":
    initializeDummyDatabase()

    app.run(debug=True)