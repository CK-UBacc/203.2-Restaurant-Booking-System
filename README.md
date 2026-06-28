# Tableflow - Restaurant booking stystem

## Overview
Table flow is a flask based web booking management system to be hosted on your servers.
It is designed to 

## Features

## Tech Stack

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
## How to Use

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

