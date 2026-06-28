# Tableflow - Restaurant booking stystem

## Overview

Table flow is a flask based web booking management system to be hosted on your servers.

It is designed to streamline the booking reservation process into a single dashboard, which allows you to keep track of your reservations from a single hub, Reducing Human error and downtime between reservations while going completely online in a growing digital world
 
## Features
 
Manage Bookings (Edit and change status)

Manage Tables (Add and remove tables to match your restaurant layout)

Admin Login (Admin Dashboard Login Connected to the database)

Email Confirmations (Upon booking with a valid email address a booking confirmation is sent to you via email)

Manage restaurant hours ( Add, remove and edit restaurant open hours)

Set new password ( Set a new password in account settings which will update in the database)

Admin Dashboard ( A dashboard that allows you to manage all other features from a single place)

Booking Form ( Booking form that can be contained in a iframe on the main restaurants website)

Statistics ( Monitor approval rates, Status breakdown for each month to adjust your restaurants open times)
 
 
## Tech Stack

Flask, SQL Alchemy For Backend
 
HTML,CSS,Java Script For Frontend
 
## Installation and Setup
### Prerequisites
- python3.12 or higher installed
- git (for cloneing and installing the repository)

### Steps
1. Clone repository:
  ```bash
  git clone https://github.com/CK-UBacc/203.2-Restaurant-Booking-System.git
  cd 203.2-Restaurant-Booking-System
  ```
2. Install dependencies.
  
    There are two options for installing dependencies
  - run "install-dependencies.bat" after installing python
  - Run the following code in the terminal
    ```bash
     pip install flask, flask_sqlalchemy, flask_mail
     ```

### How to Run (Recommended Automatic Setup)

This method installs all dependencies automatically and requires no manual pip commands

1. Download or clone this project to your computer.
2. Open the project folder.
3. Double-click the file named "run_dev_server"

The script will do the following on first run:
- Create an isolated Python environment in a folder called ".venv"
- Install all required packages automatically from requirements.txt
- Start the application server

On every run after the first, it will skip the setup and go straight to starting the server

4. Once the server is running, open a web browser and go to: http://localhost:5000

5. To stop the server, close the terminal window that opened, or press Ctrl+C inside it.

### How to Run (Manually Command Line)

If you prefer to run the app manually or the batch file does not work:

1. Open a terminal and navigate to the project folder

2. Create a virtual environment:

   python -m venv .venv

3. Activate the virtual environment:

   .venv\Scripts\activate

4. Install all required packages:

   pip install -r requirements.txt

5. Start the application:

   python run.py

6. Open a browser and go to http://localhost:5000

### Pages and URLs

The following pages are available once the app is running:

- "/"  :Landing page
- "/bookin":Public booking form for customers
- "/demo" :Demo version of the booking form
- "/demo/example" :Demo version of how real app look
- "/loginpage" :Admin login page
- "/dashboard" :Admin dashboard overview (requires login)
- "/dashboard/bookings" :Manage all bookings
- "/dashboard/restaurant-info"  :Manage tables and restaurant settings
- "/dashboard/statistics"  :Booking statistics

### Default Admin Login

When the application runs for the first time it creates a default admin account:

   Username: admin123
   Password: admin123

It is strongly recommended to change this password after your first login through the
Account Settings page in the dashboard.

## Project structure
```
203.2-Restaurant-Booking-System/
│   .gitattributes
│   .gitignore
│   config.py
│   install-dependencies.bat
│   README.md
│   run.py
│   run_dev_server.bat
│   
└───app/
    │   bookingRoutes.py
    │   dashboardRoutes.py
    │   demoRoutes.py
    │   errorRoutes.py
    │   important.py
    │   loginRoutes.py
    │   models.py
    │   routes.py
    │   __init__.py
    │   
    ├───static/
    │       bookingstyle.css
    │       style.css
    │       tableflowlogo.png
    │       
    └───templates/
            accountsettings.html
            booking.html
            bookingSuccess.html
            dashboardBase.html
            dashboardBookings.html
            dashboardOverview.html
            dashboardSettings.html
            dashboardStatistics.html
            dashboardTables.html
            error.html
            indexDemo.html
            indexMain.html
            loginpage.html
```

