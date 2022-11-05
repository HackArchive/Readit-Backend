import os
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "database.db"
UPLOAD_FOLDER = "static/images"
SECRET_KEY = "odjfhkdf;a3423"
db = SQLAlchemy()
ma = Marshmallow()

twilio_sid = os.getenv("TWILIO_SID",None)
twilio_authtoken = os.getenv("TWILIO_AUTHTOKEN",None)
twilio_number = "+14155238886"

if twilio_sid == None or twilio_authtoken == None:
    print("twilio tokens are missing \nrun export .env in terminal")
    os._exit(0)

twilio_client = Client(twilio_sid,twilio_authtoken)

