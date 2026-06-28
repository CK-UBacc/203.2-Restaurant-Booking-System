'''

'''
import secrets
def generateSecretKey():
    '''Generates a string for use as a secret key

    I don't know if this is a good way of going about this but I didn't wan't a hard coded secret key
    
    :return string: returns a string for your secret key
    '''
    return secrets.token_hex()

SQLALCHEMY_DATABASE_URI = "sqlite:///data.db"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = generateSecretKey() # For a manual secret key replace "generateSecretKey()" with a key of your choice in quote marks

# Email config 
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "tableflowproject@gmail.com"  # Email of restaurant 
MAIL_PASSWORD = "gbwh nrra vtys jyjq"  # Password in App passwords Google 