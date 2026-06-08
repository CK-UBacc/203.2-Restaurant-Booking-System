from flask import Flask
import sqlite3

app = Flask(__name__)

connection = sqlite3.connect("database.db")
cursor = connection.cursor

@app.route("/")
def index():
    return "It works!"

if __name__ == "__main__":
    app.run(debug=True)