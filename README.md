README for unfinished project

Early development web application ment to be accesed via a website
Application takes incomming bookings via web form and allows restaurants manage those bookings
Restaurants can also set up booking times and details like table availability/seating capacity

Application currently requires these installed
  -Python (I don't know which version at minimum for any of these)
  -Flask
  -Flask-SQLAlchemy

Python can be installed by downloading python from the python website and following the installation instructions
https://www.python.org/downloads/

Flask can be installed by
  1. having python installed
  2. opening up the terminal and navigating to this applications folder "203.2 - Restaurant Booking System"
  3. when in the folder "203.2 - Restaurant Booking System" runn the command "pip install flask"

Flask-SQLAlchemy can be installed by
  1. having python installed
  2. having Flask installed
  3. opening up the terminal and navigating to this applications folder "203.2 - Restaurant Booking System"
  4. when in the folder "203.2 - Restaurant Booking System" runn the command "pip install flask-sqlalchemy"

Due to the unfinished nature of the current build the applcation can only be run via command line
Navigate to the applcation folder in the terminal then run the command Python "app.py"
If application failed to run it is most likely due to one of the dependencies not being installed properly

Feature list
various html pages can be accessed via URL only (pages supposed to have navigation are currently unfinished)
URLs are:
  /booking    -The booking page restaurant guests can book through
  /dashboard  -The main dashboard for restaurant adims to manage their bookings
  /dummyData  -A testing page

This application uses
  -Python
  -Flask
  -SQLAlchemy
