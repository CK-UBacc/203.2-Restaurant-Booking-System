'''

'''
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_mail import Mail, Message
from .models import database, RestaurantSettings, Booking, Table, TimeSlot
from datetime import datetime

bookingRoute = Blueprint("booking", __name__)
mail = Mail()

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
# Routes
#-------------------------------------------------------------------------------------------------------
@bookingRoute.route("/booking", methods=["GET", "POST"]) #NEEDS: HTML page, Code
def booking():
    '''Route to booking form.
    Booking form is ment to be an embed on a page of another website so there will be no route to the booking form from our web page.

    :return render_template: template for the booking form with data for the page
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


@bookingRoute.route("/booking/success/<int:booking_id>", methods=["GET"])
def bookingSuccess(booking_id):
    '''
    
    '''
    booking = Booking.query.get_or_404(booking_id)
    return render_template("bookingSuccess.html", booking=booking)