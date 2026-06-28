'''
The applcation entry point
'''
from app import create_app
from app.models import createDatabase


app = create_app()

if __name__ == "__main__":
    createDatabase(app)

    app.run()
