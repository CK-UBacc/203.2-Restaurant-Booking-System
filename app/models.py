'''
Creates the database object and
Contains definitions for all of the database tables.
'''
#from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import datetime

#--------------------------------------------------
# Initialize database object
#--------------------------------------------------
database = SQLAlchemy()

#--------------------------------------------------
# Create many-to-many relationship between bookings and tables
#--------------------------------------------------
 
booking_tables = database.Table('booking_tables',
    database.Column('booking_id', database.Integer, database.ForeignKey('bookings.id'), primary_key=True),
    database.Column('table_id',   database.Integer, database.ForeignKey('tables.id'),   primary_key=True)
)

#--------------------------------------------------
# Database table definitions
#--------------------------------------------------

# Database "Order" was excluded due to being removed

class Table(database.Model):
    '''
    Stores information about the tables in the restaurant.

    :param int id: A unique identifier for the table.
    :param int seats: The number of seats at the table.
    :param string status: The reservation status of the table.
    '''
    __tablename__ = "tables"

    id = database.Column(database.Integer, primary_key=True)
    seats = database.Column(database.Integer)

    # AVAILABLE = free, RESERVED = has an advance booking, OCCUPIED = physically in use walk-in
    status = database.Column(database.String(20), nullable=False, default='AVAILABLE')

    def __repr__(self):
        return f"{self.id}: {self.seats}"

class Booking(database.Model):
    '''
    Stores the booking information recieved from the guest or created by an admin.

    :param int id: Unique identifier for the booking.
    :param string name: Booking name provided by the guest to identify the booking for the staff.
    :param int guestCount: Number of guests comming.
    :param string phone: Contact phone number.
    :param string email: Contact email address.
    :param date date: Scheduled date of the booking.
    :param time time: Scheduled time of the booking.
    :param string status: Current status of the booking. Accepted values: "PENDING", "APPROVED", "CANCELED", "EXPIRED".
    :param string special_requests: Any special requests for the booking.
    :param Table tables: Tables reserved in the booking
    '''
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
    
class TimeSlot(database.Model):
    '''Timeslots for bookings that can be set by a restaurant admin.

    It is assumed that restaurants will have the same fixed durration for all booking times accross different timeslots so only the start time is saved.

    :param time slot: Start time of the time slot.
    '''
    __tablename__ = "timeSlots"

    slot = database.Column(database.Time, primary_key=True)

class RestaurantSettings(database.Model): # 
    '''Restaurant-level config one row only
    
    '''
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


#user login table made in database
class User(database.Model):
    __tablename__ = "users"


    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(50), unique=True, nullable=False )
    password = database.Column(database.String(50), nullable=False)

def createDatabase(app):
    '''Creates a new database if none exists.

    :param Flask app: The current flask app.

    :return none:
    '''

    with app.app_context():
        # database.create_all() skips modifying existing tables so we don't need to check if the database exists.
        # it will either create the database and table or do nothing
        database.create_all()

        # Insert default data if table is empty
        if (RestaurantSettings.query.first() == None):
            database.session.add(RestaurantSettings(
                restaurant_name   = "RESTAURANT_NAME",
                address           = "",
                phone             = "",
                email             = "",
                description       = "DEFAULT_DESCRIPTION",
                max_party_size    = 8,
                max_advance_days  = 30,
                min_advance_hours = 2,
                open_time         = datetime.time(10, 0),
                close_time        = datetime.time(22, 0),
                days_open         = "1111100"
            ))

        # Insert default admin login if no admin login exists (essential for loging in)
        if (User.query.first() == None):
            database.session.add(User(username="admin123", password="admin123"))
        
        database.session.commit()