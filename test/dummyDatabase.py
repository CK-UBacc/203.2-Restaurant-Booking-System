'''

'''
from app.models import Table, Booking, TimeSlot, User, RestaurantSettings
import datetime
def initializeDummyDatabase(app, database): # Crate dummy database file with dummy data in tables
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


        #Created the default admin login
        database.session.add_all([
            User(username="admin123", password="admin123"),
            User(username="admin321", password="admin321")

        ])
            
        

        print("COMMITING TABLE CHANGES")
        database.session.commit()
    
        print("DUMMY DATABASE INITIALIATION COMPLETE")