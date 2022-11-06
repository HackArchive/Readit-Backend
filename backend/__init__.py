import os
import schedule
from flask import Flask
from flask_login import LoginManager
from extensions import UPLOAD_FOLDER,DB_NAME,SECRET_KEY,db,ma
from time import sleep
from threading import Thread
from twilio.rest import Client 

def create_app():

    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    db.init_app(app)

    from backend.auth import auth 
    from backend.views import views

    app.register_blueprint(views,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/auth/')


    from backend.models import (
        User,
        Book,
        Chapter
    )

    create_database(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


    # serialize/deserialize library 
    ma.init_app(app)    

    scheduling_thread = Thread(target=run_schedular,args=[app,])
    scheduling_thread.start()

    return app


def run_schedular(app):

    while True:
        with app.app_context():
            schedule.run_pending()
        sleep(1) 

def create_database(app):

    if not os.path.exists(DB_NAME):
        with app.app_context():
            db.create_all()
        print("database created...")