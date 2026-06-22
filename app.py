from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
# import os # not currently being used?
import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SLQALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

# Email config 
app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USERNAME"] = "tableflowproject@gmail.com"  # Email of restaurant 
app.config["MAIL_PASSWORD"] = "gbwh nrra vtys jyjq"  # Password in App passwords Google 

database = SQLAlchemy(app)
mail = Mail(app)

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

class RestaurantSettings(database.Model): # Restaurant-level config one row only
    __tablename__ = "restaurant_settings"

    id                = database.Column(database.Integer, primary_key=True)
    restaurant_name   = database.Column(database.String(128),  default="My Restaurant")
    address           = database.Column(database.String(256))
    phone             = database.Column(database.String(32))
    email             = database.Column(database.String(128))
    description       = database.Column(database.String(512))  # shown on public booking form
    max_party_size    = database.Column(database.Integer,      default=8)
    max_advance_days  = database.Column(database.Integer,      default=30)
    min_advance_hours = database.Column(database.Integer,      default=2)
    open_time         = database.Column(database.Time,         default=datetime.time(10, 0))
    close_time        = database.Column(database.Time,         default=datetime.time(22, 0))
    days_open         = database.Column(database.String(7),    default="1111100") # Mon-Sun, 1=open 0=closed

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

        print("INSERTING DEFAULT SETTINGS")
        database.session.add(RestaurantSettings(
            restaurant_name   = "TableFlow Demo",
            address           = "123 Main Street",
            phone             = "04 0000 0000",
            email             = "hello@tableflow.com",
            description       = "Welcome! We look forward to having you.",
            max_party_size    = 8,
            max_advance_days  = 30,
            min_advance_hours = 2,
            open_time         = datetime.time(10, 0),
            close_time        = datetime.time(22, 0),
            days_open         = "1111100"
        ))

        print("COMMITING TABLE CHANGES")
        database.session.commit()
    
        print("DUMMY DATABASE INITIALIATION COMPLETE")

#-------------------------------------------------------------------------------------------------------
# Email helper
#-------------------------------------------------------------------------------------------------------
def send_booking_confirmation(booking, settings):
    # Skip if customer has no email or SMTP is not configure
    if not booking.email or not app.config.get("MAIL_USERNAME"):
        return
    try:
        restaurant_name = settings.restaurant_name if settings else "Restaurant"
        msg = Message(
            subject=f"Booking Received - {restaurant_name}",
            sender=app.config["MAIL_USERNAME"],
            recipients=[booking.email]
        )
        msg.body = (
            f"Hi {booking.name},\n\n"
            f"Thank you for your reservation at {restaurant_name}.\n\n"
            f"Booking details:\n"
            f"  Date:   {booking.date.strftime('%A, %d %B %Y')}\n"
            f"  Time:   {booking.time.strftime('%I:%M %p')}\n"
            f"  Guests: {booking.guestCount}\n"
            f"  Status: Pending\n\n"
            f"We will be in touch shortly to confirm your reservation.\n\n"
            + (f"Phone:   {settings.phone}\n" if settings and settings.phone else "")
            + (f"Address: {settings.address}\n" if settings and settings.address else "")
            + f"\n{restaurant_name}"
        )
        mail.send(msg)
        print(f"Confirmation email sent to {booking.email}")
    except Exception as e:
        print(f"Email send failed: {e}")

#-------------------------------------------------------------------------------------------------------
# Context processor injects restaurant_settings into every template automatically
#-------------------------------------------------------------------------------------------------------
@app.context_processor
def inject_settings():
    try:
        settings = RestaurantSettings.query.first()
    except Exception:
        settings = None
    return dict(restaurant_settings=settings)

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
    #return redirect(url_for("dashboard"))

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
            time = datetime.datetime.strptime(request.form.get("time"), "%H:%M:%S").time()
            print(f"\tTime recieved: {time}")

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

            send_booking_confirmation(newBooking, RestaurantSettings.query.first())

        except Exception as e:
            print(f"ERROR! {str(e)}")
    
    # Get all the data to display on the page
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
    today = datetime.date.today()
    today_bookings = Booking.query.filter_by(date=today).all()
    today_approved = [b for b in today_bookings if b.status.upper() == "APPROVED"]
    today_guests = sum(b.guestCount for b in today_approved)
    total_seats = sum(t.seats for t in tables)
    return render_template(
        "dashboardTables.html",
        tables=tables,
        today_bookings=today_bookings,
        today_approved_count=len(today_approved),
        today_guests=today_guests,
        total_seats=total_seats,
        active="tables"
    )

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

@app.route("/dashboard/statistics", methods=["GET"])
def dashboardStatistics():
    bookings = Booking.query.all()

    status_counts = {"PENDING": 0, "APPROVED": 0, "CANCELED": 0, "EXPIRED": 0}
    for b in bookings:
        s = b.status.upper()
        if s in status_counts:
            status_counts[s] += 1

    monthly_raw = {}
    for b in bookings:
        key = b.date.strftime("%b %Y")
        monthly_raw[key] = monthly_raw.get(key, 0) + 1

    monthly = [
        {"label": k, "count": v}
        for k, v in sorted(monthly_raw.items(), key=lambda x: datetime.datetime.strptime(x[0], "%b %Y"))
    ]

    approved_guests = sum(b.guestCount for b in bookings if b.status.upper() == "APPROVED")
    max_monthly = max((m["count"] for m in monthly), default=0)
    max_status = max(status_counts.values(), default=0)

    return render_template(
        "dashboardStatistics.html",
        bookings=bookings,
        status_counts=status_counts,
        monthly=monthly,
        approved_guests=approved_guests,
        max_monthly=max_monthly,
        max_status=max_status,
        active="statistics"
    )

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
# Settings routes
#-------------------------------------------------------------------------------------------------------
@app.route("/dashboard/settings", methods=["GET", "POST"])
def dashboardSettings():
    settings = RestaurantSettings.query.first()
    if not settings: # create default row if missing
        settings = RestaurantSettings()
        database.session.add(settings)
        database.session.commit()

    if request.method == "POST":
        section = request.form.get("section", "")
        try:
            if section == "info":
                settings.restaurant_name = request.form.get("restaurant_name", "").strip() or settings.restaurant_name
                settings.address         = request.form.get("address",   "").strip() or None
                settings.phone           = request.form.get("phone",     "").strip() or None
                settings.email           = request.form.get("email",     "").strip() or None
                settings.description     = request.form.get("description","").strip() or None

            elif section == "rules":
                settings.max_party_size    = int(request.form.get("max_party_size",    settings.max_party_size))
                settings.max_advance_days  = int(request.form.get("max_advance_days",  settings.max_advance_days))
                settings.min_advance_hours = int(request.form.get("min_advance_hours", settings.min_advance_hours))

            elif section == "hours":
                settings.open_time  = datetime.time.fromisoformat(request.form.get("open_time",  "10:00"))
                settings.close_time = datetime.time.fromisoformat(request.form.get("close_time", "22:00"))
                days = ""
                for d in ["mon","tue","wed","thu","fri","sat","sun"]:
                    days += "1" if request.form.get(d) else "0"
                settings.days_open = days

            database.session.commit()
            flash("Settings saved.", "success")
        except Exception as e:
            print(f"ERROR! {str(e)}")
            flash("Failed to save settings.", "error")

    timeSlots = TimeSlot.query.order_by(TimeSlot.slot).all()
    return render_template("dashboardSettings.html", settings=settings, timeSlots=timeSlots, active="settings")


@app.route("/dashboard/settings/timeslots/add", methods=["POST"])
def dashboardTimeSlotAdd():
    try:
        slot_str = request.form.get("slot") # "HH:MM" from <input type="time">
        slot = datetime.time.fromisoformat(slot_str)
        if not TimeSlot.query.get(slot):
            database.session.add(TimeSlot(slot=slot))
            database.session.commit()
            flash("Time slot added.", "success")
        else:
            flash("Time slot already exists.", "error")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Invalid time format.", "error")
    return redirect(url_for("dashboardSettings"))


@app.route("/dashboard/settings/timeslots/delete", methods=["POST"])
def dashboardTimeSlotDelete():
    try:
        slot_str = request.form.get("slot") # "HH:MM:SS" from hidden field
        slot = datetime.time.fromisoformat(slot_str)
        ts = TimeSlot.query.get(slot)
        if ts:
            database.session.delete(ts)
            database.session.commit()
            flash("Time slot removed.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to remove time slot.", "error")
    return redirect(url_for("dashboardSettings"))


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