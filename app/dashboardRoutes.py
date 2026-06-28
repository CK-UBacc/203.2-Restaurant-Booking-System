'''
Route blueprints for the admin dashboard pages
'''

from flask import Blueprint, session, redirect, url_for, render_template, request, flash
from .models import database, Table, Booking, TimeSlot, RestaurantSettings, User
import datetime
import calendar as cal_module

#--------------------------------------------------
# Dashboard blueprint object
#--------------------------------------------------
dashboard = Blueprint("dashboard", __name__)

#--------------------------------------------------
# Dashboard overview page
#--------------------------------------------------

# Dashboard overview function name needed to be changed from dashboard to dashboard index as dashboard is now being used for the blueprint name
# This will cause problems but aeugh.

#Displays main dashboard overview and shows todays bookings
@dashboard.route("", methods=["GET"])
def dashboardIndex():
    '''Route to dashboard

    Dashboard is supposed to display the restaurants data and act as the hub page for a restaurant manager/admin

    :return render_template: Template for the dashboard with all of the data for it.
    '''
    if not session.get("logged_in"):
        return redirect(url_for("login.loginpage"))
    

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

#--------------------------------------------------
# Booking management
#--------------------------------------------------
@dashboard.route("/bookings", methods=["GET"])
#Displays all bookings so the admin can view and manage them
def dashboardBookings():
    '''Route to the manage bookings page of the dashboard.

    :return render_template: Template for the manage bookings page with all bookings.
    '''
    if not session.get("logged_in"):
        return redirect(url_for("login.loginpage"))
    
    bookings = Booking.query.all()
    timeSlots = TimeSlot.query.all()
    tables = Table.query.all()
    return render_template("dashboardBookings.html", bookings=bookings, timeSlots=timeSlots, tables=tables, active="bookings")

@dashboard.route("/bookings/add", methods=["POST"])
def dashboardBookingsAdd(): #Creates new booking from admin dashboard and saves it to the database
    '''Create a new booking record in the database

    New bookings show "PENDING" status by default though it can be changed to "APPROVED" on the restaurant-info page.
    
    :return redirect: Redirects the user to bookings dashboard
    '''

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

    return redirect(url_for("dashboard.dashboardBookings"))

@dashboard.route("/bookings/approve/<int:id>", methods=["POST"])
def dashboardBookingsApprove(id): #Approves a selected booking by changing the status to approved
    '''Quickly approves a pending booking by setting status to APPROVED
    
    :return redirect: Redirects to the dashboard overview page
    '''
    try:
        booking = Booking.query.get_or_404(id)
        booking.status = "APPROVED"
        database.session.commit()
        flash("Booking approved.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to approve booking.", "error")
    return redirect(url_for("dashboard.dashboardIndex"))

@dashboard.route("/bookings/edit/<int:id>", methods=["POST"])
def dashboardBookingsEdit(id): #Updates an existing booking with details entered in by the admin
    '''Updates all fields of an exist booking (name, email, phone, guest count,date, time, and status)
    
    :return redirect: Redirects to the bookings dashboard
    '''
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
    return redirect(url_for("dashboard.dashboardBookings"))

#--------------------------------------------------
# Restaurant-info management
#--------------------------------------------------

# Restaurant-info page was initialy just table management but other mangagment features where merged into it
# as the table management page was supposed to manage the restaurant settings.
# this is why all the functions are called some variation of "dashboardTable"
@dashboard.route("/restaurant-info", methods=["GET", "POST"])
def dashboardTables(): #Displays and updates restuarant info, table settings and booking rules + opening hours
    '''Route to the manage tables page of the dashboard.
    Also handles settings POST requests (merged from dashboardSettings).

    :return redirect: Redirects to restaurant-info
    :return render_template: Template for the manage tables page with all tables.
    '''
    if not session.get("logged_in"):
        return redirect(url_for("login.loginpage"))
    
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

        return redirect(url_for("dashboard.dashboardTables"))

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

@dashboard.route("/restaurant-info/add", methods=["POST"])
def dashboardTablesAdd(): #Add new tables to the restuarant floor plan with a set number of seats assigned to the table by the admin
    '''Creates a new table record with the specific seat count
    
    :return redirect: Redirects to the restaurant-info dashboard.
    '''
    try:
        seats = int(request.form.get("seats"))
        database.session.add(Table(seats=seats))
        database.session.commit()
        flash("Table added successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to add table.", "error")
    return redirect(url_for("dashboard.dashboardTables"))

@dashboard.route("/restaurant-info/edit/<int:id>", methods=["POST"])
def dashboardTablesEdit(id): #Updates the seat count for restaurant tables that already exist 
    '''Updates the seat number in existing table.
    
    :param int id: ID of the table.

    :return redirect: Redirects to the Restaurant-info dashboard.
    '''
    try:
        table = Table.query.get_or_404(id)
        table.seats = int(request.form.get("seats"))
        database.session.commit()
        flash("Table updated successfully.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to update table.", "error")
    return redirect(url_for("dashboard.dashboardTables"))

# Is this even used anymore?
@dashboard.route("/restaurant-info/toggle/<int:id>", methods=["POST"])
def dashboardTablesToggle(id): #Changes tables status from available to reserved or canceled 
    '''Manually set table status (AVAILABLE / RESERVED / OCCUPIED)

    :param int id: ID of the table.

    :return redirect: Redirects to the Restaurant-info dashboard.
    '''
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
    return redirect(url_for("dashboard.dashboardTables"))

@dashboard.route("/restaurant-info/delete/<int:id>", methods=["POST"])
def dashboardTablesDelete(id): #Deleted table selected by the admin. from the existing table availability.
    '''Delete a table

    :param int id: ID of the table.

    :return redirect: Redirects to the Restaurant-info dashboard.
    '''
    try:
        table = Table.query.get_or_404(id)
        database.session.delete(table)
        database.session.commit()
        flash("Table deleted.", "success")
    except Exception as e:
        print(f"ERROR! {str(e)}")
        flash("Failed to delete table.", "error")
    return redirect(url_for("dashboardTables"))

@dashboard.route("/settings/timeslots/add", methods=["POST"])
def dashboardTimeSlotAdd(): #Adds a new time slot to the restuaruants settings
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
    return redirect(url_for("dashboard.dashboardTables"))


@dashboard.route("/settings/timeslots/delete", methods=["POST"])
def dashboardTimeSlotDelete(): #Removes and existing time slot from the restaurants settings
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
    return redirect(url_for("dashboard.dashboardTables"))

#--------------------------------------------------
# Statistics page
#--------------------------------------------------
@dashboard.route("/statistics", methods=["GET"])
def dashboardStatistics(): #Displays booking stats, Such as total,group size etc 
    '''
    
    :return render_template: Template for the statistics page and all of the data for it
    '''
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

    all_bookings = Booking.query.all()

    # Compute fixed period counts for stat cards
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end   = week_start + datetime.timedelta(days=6)
    month_start = today.replace(day=1)
    month_end   = today.replace(day=cal_module.monthrange(today.year, today.month)[1])

    today_count = sum(1 for b in all_bookings if b.date == today)
    week_count  = sum(1 for b in all_bookings if week_start <= b.date <= week_end)
    month_count = sum(1 for b in all_bookings if month_start <= b.date <= month_end)
    all_count   = len(all_bookings)

    # Filter bookings for the detailed breakdown section
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
        today_count=today_count,
        week_count=week_count,
        month_count=month_count,
        all_count=all_count,
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

#--------------------------------------------------
# Settings page
#--------------------------------------------------



#-------------------------------------------------
#Save Password changes & Account Settings Route
#-------------------------------------------------

@dashboard.route("/accountsettings")
def accountsettings():
    return render_template("accountsettings.html", active="Accountsettings")

@dashboard.route("/change-password", methods=["POST"])
def dashboardChangePassword():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    user = User.query.filter_by(username=session["username"]).first()

    if user.password != current_password:
        flash("Current Password is Incorrect")
        return redirect(url_for("dashboard.dashboardTables"))
    
    if new_password != confirm_password:
        flash("Passwords do not match")
        return redirect(url_for("dashboard.dashboardTables"))
    
    user.password = new_password
    database.session.commit()

    flash("Password has been changed")
    return redirect(url_for("dashboard.dashboardTables"))

