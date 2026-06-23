from modules import create_app
from tests.dummyDatabase import * # Importing the dummy data and debug funcitons remove in final product
from modules.models import database


app = create_app()

if __name__ == "__main__":
    initializeDummyDatabase(app, database)

    app.run(debug=True)