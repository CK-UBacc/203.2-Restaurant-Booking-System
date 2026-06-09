from flask import Flask, render_template, redirect
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

    def __repr__(self):
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
                date=datetime.datetime.now().date(),
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

@app.route("/dashboard/<int:id>", methods=["GET"]) #NEEDS: HTML pass, code
def dashboard(id):
    return render_template("dashboard.html", id=id)

if __name__ == "__main__":
    initializeDummyDatabase()

    app.run(debug=True)