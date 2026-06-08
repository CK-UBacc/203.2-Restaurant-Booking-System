from flask import Flask, render_template, redirect
import sqlite3
import os

app = Flask(__name__)

def createDatabase():
    '''
    I don't know what this does yet but I'll write a propper thing when its done

    '''
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor

@app.route("/")
def index():
    '''
    Route to home page.

    Args:
    None

    Returns:
    render_template: template for the home page

    '''
    return render_template('index.html')

@app.route("/booking/<int:id>", methods=["GET", "POST"]) #NEEDS: HTML page
def booking(id):
    '''
    Route to booking form.
    Booking form is ment to be an embed on a page of another website so there will be no route to the booking form from our web page.

    Args:
    id (int): restaurant ID

    Returns:
    render_template: template for the booking form

    '''
    return render_template()

if __name__ == "__main__":
    app.run(debug=True)