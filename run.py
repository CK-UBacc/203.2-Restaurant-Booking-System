'''
The applcation entry point
'''
from app import create_app
from test.dummyDatabase import * # Importing the dummy data and debug funcitons remove in final product
from app.models import database


app = create_app()

if __name__ == "__main__":
    #initializeDummyDatabase(app, database)

    app.run(debug=True)
