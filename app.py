from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_mail import Mail, Message
from wtformsTesting import TestBookingForm
# import os # not currently being used?
import datetime
import calendar as cal_module
from wtformsTesting import TestBookingForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dummy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-for-flash-messages" # I forgot what the secret key is but it is super important

# Email config 
app.config["MAIL_SERVER"]   = "smtp.gmail.com"
app.config["MAIL_PORT"]     = 587
app.config["MAIL_USE_TLS"]  = True
app.config["MAIL_USERNAME"] = "tableflowproject@gmail.com"  # Email of restaurant 
app.config["MAIL_PASSWORD"] = "gbwh nrra vtys jyjq"  # Password in App passwords Google 

from datetime import timedelta #Sets remember me time duration to 30 days
app.permanent_session_lifetime = timedelta(days=30) #Tells flask how long a single session can be live for
database = SQLAlchemy(app)
mail = Mail(app)

#-------------------------------------------------------------------------------------------------------
# Database tables stuff
#
# Don't know how this could be used to create different tables for different restaurants. I'll figure it out
#-------------------------------------------------------------------------------------------------------

# Many-to-many relationship between bookings and tables
booking_tables = database.Table('booking_tables',
    database.Column('booking_id', database.Integer, database.ForeignKey('bookings.id'), primary_key=True),
    database.Column('table_id',   database.Integer, database.ForeignKey('tables.id'),   primary_key=True)
)

class Table(database.Model):
    __tablename__ = "tables"

    id = database.Column(database.Integer, primary_key=True)
    seats = database.Column(database.Integer)

    # AVAILABLE = free, RESERVED = has an advance booking, OCCUPIED = physically in use walk-in
    status = database.Column(database.String(20), nullable=False, default='AVAILABLE')

    def __repr__(self):
        return f"{self.id}: {self.seats}"

class Booking(database.Model):
    __tablename__ = "bookings"

    id = database.Column(database.Integer, primary_key=True)
    name = database.Column(database.String(128), nullable=False)
    guestCount = database.Column(database.Integer, default=1)
    phone = database.Column(database.String(32))
    email = database.Column(database.String(128))
    date = database.Column(database.Date, nullable=False)
    time = database.Column(database.Time, nullable=False)
    status           = database.Column(database.String(16),  nullable=False)
    special_requests = database.Column(database.String(512))
    # Many-to-many relationship with Table via booking_tables 
    tables = database.relationship('Table', secondary=booking_tables, backref='bookings')

    def __repr__(self): # I don't know how to set up the __repr__
        return f"{self.id}: {self.name}"
    
class Order(database.Model):
    __tablename__ = "orders"

    id         = database.Column(database.Integer, primary_key=True)
    table_id   = database.Column(database.Integer, database.ForeignKey('tables.id'), nullable=True)
    status       = database.Column(database.String(20), nullable=False, default='OPEN')  # OPEN / PAID / CANCELED
    created_at   = database.Column(database.DateTime, default=datetime.datetime.now)
    note         = database.Column(database.String(256))
    payment_cash = database.Column(database.Float, nullable=False, default=0.0)
    payment_card = database.Column(database.Float, nullable=False, default=0.0)
    table      = database.relationship('Table', backref='pos_orders')
    items      = database.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(oi.quantity * oi.unit_price for oi in self.items)

    def __repr__(self):
        return f"Order {self.id}"

class OrderItem(database.Model):
    __tablename__ = "order_items"

    id           = database.Column(database.Integer, primary_key=True)
    order_id     = database.Column(database.Integer, database.ForeignKey('orders.id'),      nullable=False)
    quantity     = database.Column(database.Integer, nullable=False, default=1)

    def __repr__(self):
        return f"OrderItem {self.id}"

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
    max_party_size    = database.Column(database.Integer,default=8)
    max_advance_days  = database.Column(database.Integer,default=30)
    min_advance_hours = database.Column(database.Integer,default=2)
    open_time         = database.Column(database.Time,default=datetime.time(10, 0))
    close_time        = database.Column(database.Time,default=datetime.time(22, 0))
    days_open         = database.Column(database.String(7),default="1111100") # Mon-Sun, 1=open 0=closed
    auto_confirm      = database.Column(database.Boolean,default=False)# auto approve new bookings

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
                time=datetime.time(12, 0),
                status="PENDING"),
            Booking(
                name="Jamie Jackson",
                guestCount=3,
                phone="0404040",
                email="dummy@email.email.email",
                date=datetime.date.today(),
                time=datetime.time(11, 0),
                status="EXPIRED"),
            Booking(
                name="Jackie Chan",
                guestCount=2,
                phone="8456215",
                email="Thebest@email.email.email",
                date=datetime.date.today(),
                time=datetime.time(13, 30),
                status="APPROVED"),
            Booking(
                name="Your mum",
                guestCount=5,
                phone="4567892",
                email="fatass@email.email.email",
                date=datetime.date.today(),
                time=datetime.time(18, 0),
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
    
        # Link bookings to tables
        dummyBookings[0].tables = [dummyTables[0]]  # Jimmy Johnson in Table 1 
        dummyBookings[2].tables = [dummyTables[2]]  # Jackie Chan in Table 3

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
    # Skip if customer has no email 
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
            f"  Status: Pending\n"
            + (f"  Special Requests: {booking.special_requests}\n" if booking.special_requests else "")
            + f"\nWe will be in touch shortly to confirm your reservation.\n\n"
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
    restaurant_settings = RestaurantSettings.query.first()
    return render_template('indexMain.html', restaurant_settings=restaurant_settings)
    #return redirect(url_for("dashboard"))

@app.route("/demo")
def indexDemo():
    '''
    Route to restaurant demo page.
    Shows what a restaurant booking page looks like using TableFlow.
    '''
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    today = datetime.date.today()
    restaurant_settings = RestaurantSettings.query.first()
    return render_template('indexDemo.html', timeSlots=timeSlots, tables=tables, today=today, restaurant_settings=restaurant_settings)

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

            cfg = RestaurantSettings.query.first()
            booking_status = "APPROVED" if (cfg and cfg.auto_confirm) else "PENDING"
            newBooking = Booking(
                name=name,
                guestCount=guestCount,
                email=email,
                phone=phone,
                date=date,
                time=time,
                status=booking_status,
                special_requests=request.form.get("special_requests", "").strip() or None)

            # Assign preferred table if customer selected one
            preferred_table_id = request.form.get("preferred_table_id")
            if preferred_table_id:
                table = Table.query.get(int(preferred_table_id))
                if table:
                    newBooking.tables.append(table)

            database.session.add(newBooking)
            database.session.commit()

            send_booking_confirmation(newBooking, RestaurantSettings.query.first())

            return redirect(url_for("bookingSuccess", booking_id=newBooking.id))

        except Exception as e:
            print(f"ERROR! {str(e)}")
            flash("Something went wrong. Please check your details and try again.", "error")

    # Get all the data to display on the page
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    today = datetime.date.today()

    return render_template("booking.html", timeSlots=timeSlots, tables=tables, today=today)


@app.route("/booking/success/<int:booking_id>", methods=["GET"])
def bookingSuccess(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template("bookingSuccess.html", booking=booking)

@app.route("/dashboard", methods=["GET"]) #NEEDS: HTML pass, code  # ID may not be needed in the URL
def dashboard():

    if not session.get("logged_in"):
        return redirect(url_for("loginpage"))
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
    today = datetime.date.today()

    # Compute today's table statuses for the overview floor plan
    today_bookings = Booking.query.filter_by(date=today).all()
    reserved_ids = set()
    for booking in today_bookings:
        if booking.status.upper() in ("PENDING", "APPROVED"):
            for table in booking.tables:
                reserved_ids.add(table.id)

    table_statuses = {}
    for t in tables:
        if t.status == 'OCCUPIED':
            table_statuses[t.id] = 'OCCUPIED'
        elif t.id in reserved_ids:
            table_statuses[t.id] = 'RESERVED'
        else:
            table_statuses[t.id] = 'AVAILABLE'

    return render_template("dashboardOverview.html", bookings=bookings, tables=tables, table_statuses=table_statuses, active="overview")



@app.route("/dashboard/bookings", methods=["GET"])
def dashboardBookings():

    if not session.get("logged_in"):
        return redirect(url_for("loginpage"))
    '''
    Route to the manage bookings page of the dashboard.

    Args:
    None

    Returns:
    render_template: template for the manage bookings page with all bookings.
    '''
    bookings = Booking.query.all()
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    return render_template("dashboardBookings.html", bookings=bookings, timeSlots=timeSlots, tables=tables, active="bookings")

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
            status="PENDING",
            special_requests=request.form.get("special_requests", "").strip() or None)

        # Assign selected tables to the booking
        table_ids = request.form.getlist('table_ids')
        for tid in table_ids:
            table = Table.query.get(int(tid))
            if table:
                newBooking.tables.append(table)

        database.session.add(newBooking)
        database.session.commit()
        flash("Booking added successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to add booking. Please check all fields.", "error")

    return redirect(url_for("dashboardBookings"))

@app.route("/dashboard/bookings/approve/<int:id>", methods=["POST"])  # Quickly approves a pending booking by setting status to APPROVED
def dashboardBookingsApprove(id):

    try:
        booking = Booking.query.get_or_404(id)
        booking.status = "APPROVED"
        database.session.commit()
        flash("Booking approved.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to approve booking.", "error")
    return redirect(url_for("dashboard"))

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
        booking.status           = request.form.get("status")
        booking.special_requests = request.form.get("special_requests", "").strip() or None

        # Update table assignment clear old and assign new selected tables
        booking.tables = []
        table_ids = request.form.getlist('table_ids')
        for tid in table_ids:
            table = Table.query.get(int(tid))
            if table:
                booking.tables.append(table)

        database.session.commit()
        flash("Booking updated successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to update booking.", "error")
    return redirect(url_for("dashboardBookings"))

@app.route("/dashboard/tables", methods=["GET", "POST"])
def dashboardTables():

    if not session.get("logged_in"):
        return redirect(url_for("loginpage"))
    '''
    Route to the manage tables page of the dashboard.
    Also handles settings POST requests (merged from dashboardSettings).

    Args:
    None

    Returns:
    render_template: template for the manage tables page with all tables.
    '''
    settings = RestaurantSettings.query.first()
    if not settings:
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
                settings.min_advance_hours = int(request.form.get("min_advance_hours", settings.min_advance_hours))

            elif section == "hours":
                settings.open_time  = datetime.time.fromisoformat(request.form.get("open_time",  "10:00"))
                settings.close_time = datetime.time.fromisoformat(request.form.get("close_time", "22:00"))
                days = ""
                for d in ["mon","tue","wed","thu","fri","sat","sun"]:
                    days += "1" if request.form.get(d) else "0"
                settings.days_open = days

            elif section == "booking_automation":
                settings.auto_confirm = request.form.get("auto_confirm") == "1"

            database.session.commit()
            flash("Settings saved.", "success")
        except Exception as e:
            print(f"ERROR! {str(e)}")
            flash("Failed to save settings.", "error")

        return redirect(url_for("dashboardTables"))

    tables = Table.query.all()
    today = datetime.date.today()

    # Use selected date from query param, fallback to today
    date_str = request.args.get("date")
    try:
        selected_date = datetime.date.fromisoformat(date_str) if date_str else today
    except ValueError:
        selected_date = today

    is_today = (selected_date == today)

    # Get bookings for the selected date
    date_bookings = Booking.query.filter_by(date=selected_date).all()

    # Find which tables have an active booking on the selected date
    reserved_ids = set()
    for booking in date_bookings:
        if booking.status.upper() in ("PENDING", "APPROVED"):
            for table in booking.tables:
                reserved_ids.add(table.id)

    # 3 status: RESERVED, OCCUPIED, AVAILABLE
    table_statuses = {}
    for t in tables:
        if is_today and t.status == 'OCCUPIED':
            table_statuses[t.id] = 'OCCUPIED'
        elif t.id in reserved_ids:
            table_statuses[t.id] = 'RESERVED'
        else:
            table_statuses[t.id] = 'AVAILABLE'

    total_seats     = sum(t.seats for t in tables)
    available_count = sum(1 for s in table_statuses.values() if s == 'AVAILABLE')
    reserved_count  = sum(1 for s in table_statuses.values() if s == 'RESERVED')
    occupied_count  = sum(1 for s in table_statuses.values() if s == 'OCCUPIED')

    timeSlots = TimeSlot.query.order_by(TimeSlot.slot).all()

    return render_template(
        "dashboardTables.html",
        tables=tables,
        table_statuses=table_statuses,
        date_bookings=date_bookings,
        selected_date=selected_date,
        is_today=is_today,
        total_seats=total_seats,
        available_count=available_count,
        reserved_count=reserved_count,
        occupied_count=occupied_count,
        settings=settings,
        timeSlots=timeSlots,
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

@app.route("/dashboard/tables/toggle/<int:id>", methods=["POST"])  # Manually set table status (AVAILABLE / RESERVED / OCCUPIED)
def dashboardTablesToggle(id):
    try:
        table = Table.query.get_or_404(id)
        new_status = request.form.get("new_status", "AVAILABLE")
        if new_status in ('AVAILABLE', 'RESERVED', 'OCCUPIED'):
            table.status = new_status
            database.session.commit()
            flash(f"Table marked as {new_status.capitalize()}.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to update table status.", "error")
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
    period = request.args.get("period", "all")
    today = datetime.date.today()

    # get date from the date picker if theres one
    date_str = request.args.get("date")
    selected_date = None
    if date_str:
        try:
            selected_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            pass

    ref_date = selected_date if selected_date else today
    is_today = (selected_date is None or selected_date == today)

    if selected_date:
        date_start = selected_date
        date_end = selected_date
    elif period == "today":
        date_start = today
        date_end = today
    elif period == "week":
        # week starts monday i think
        date_start = today - datetime.timedelta(days=today.weekday())
        date_end = date_start + datetime.timedelta(days=6)
    elif period == "month":
        date_start = today.replace(day=1)
        date_end = today.replace(day=cal_module.monthrange(today.year, today.month)[1])
    else:
        date_start = None
        date_end = None

    bookings_query = Booking.query
    if date_start:
        bookings_query = bookings_query.filter(Booking.date >= date_start)
    if date_end:
        bookings_query = bookings_query.filter(Booking.date <= date_end)
    bookings = bookings_query.all()

    total = len(bookings)
    approved_count = sum(1 for b in bookings if b.status == 'APPROVED')
    pending_count = sum(1 for b in bookings if b.status == 'PENDING')
    canceled_count = sum(1 for b in bookings if b.status == 'CANCELED')
    expired_count = sum(1 for b in bookings if b.status == 'EXPIRED')

    approval_rate = round(approved_count / total * 100) if total > 0 else 0
    upcoming_count = sum(1 for b in bookings if b.date >= today and b.status in ('APPROVED', 'PENDING'))
    avg_group_size = round(sum(b.guestCount for b in bookings) / total, 1) if total > 0 else 0 # not sure if this should round or not

    status_breakdown = [
        ('Approved', approved_count),
        ('Pending', pending_count),
        ('Canceled', canceled_count),
        ('Expired', expired_count),
    ]
    max_status_count = max((c for _, c in status_breakdown), default=1)

    slot_counts = {}
    for b in bookings:
        label = b.time.strftime('%I:%M %p')
        slot_counts[label] = slot_counts.get(label, 0) + 1
    top_slots = sorted(slot_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    max_slot_count = top_slots[0][1] if top_slots else 1

    recent_bookings = sorted(bookings, key=lambda b: b.date, reverse=True)[:10]

    return render_template(
        "dashboardStatistics.html",
        period=period,
        selected_date=selected_date,
        ref_date=ref_date,
        is_today=is_today,
        total=total,
        approved_count=approved_count,
        approval_rate=approval_rate,
        upcoming_count=upcoming_count,
        avg_group_size=avg_group_size,
        status_breakdown=status_breakdown,
        max_status_count=max_status_count,
        top_slots=top_slots,
        max_slot_count=max_slot_count,
        recent_bookings=recent_bookings,
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
    testBooking = TestBookingForm()
    testBooking.process()

    return render_template("dummyDataDisplay.html", 
                           tables=tables, 
                           bookings=bookings,
                           timeSlots=timeSlots,
                           testBooking=testBooking
                           )

@app.route("/loginpage", methods=["GET","POST"])
def loginpage():
    if request.method == "POST":

        username = request.form.get("AdminUsername")
        password = request.form.get("Adminpassword")

        remember_me = request.form.get("remember_me") == "on"

        if username == "admin123" and password == "admin123":
            session["logged_in"] = True
            session["username"] = username

            session.permanent = remember_me

            return redirect(url_for("dashboard"))
        
        return render_template("loginpage.html",
                               error="Incorrect Username Or Password"
            )
       
    return render_template("loginpage.html")

@app.route("/Logout")
def logout():
    session.clear

    return redirect(url_for("loginpage"))


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
@app.route("/dashboard/settings", methods=["GET","POST"])
def dashboardSettings():
    # Settings page merged into Manage Tables
    return redirect(url_for("dashboardTables"))


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
    return redirect(url_for("dashboardTables"))


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
    return redirect(url_for("dashboardTables"))


#-------------------------------------------------------------------------------------------------------
# API returns JSON data for frontend use
#-------------------------------------------------------------------------------------------------------
@app.route("/api/availability")  # Retuns table availability
def apiAvailability():
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