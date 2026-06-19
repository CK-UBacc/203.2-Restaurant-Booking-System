'''
models.py
'''
from flask_sqlalchemy import SQLAlchemy

database = SQLAlchemy()

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
    date = database.Column(database.Date, nullable=False)
    time = database.Column(database.Time, nullable=False)
    table = database.Column(database.Integer, database.ForeignKey(Table.id))
    status = database.Column(database.String(16), nullable=False)

    def __repr__(self): # I don't know how to set up the __repr__
        return f"{self.id}: {self.name}"
    
class TimeSlot(database.Model): # 
    __tablename__ = "timeSlots"

    slot = database.Column(database.Time, primary_key=True)