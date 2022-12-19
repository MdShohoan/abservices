import uuid
import datetime
import random
import math as m
#we import waitress here. 
#from waitress import serve

from flask_migrate import Migrate
from flask import Flask,session,current_app 
from flask_wtf.csrf import CSRFProtect,generate_csrf
#from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import CSRFError
from config import DevelopmentConfig

# import extensions instance
from app.models import db
from app.models import OTPModel
from flask_mail import Mail

import logging
from logging.handlers import TimedRotatingFileHandler

# instance of migrate flask
migrate = Migrate()
mail = Mail()
#initialize log 
current_date = datetime.datetime.now().strftime("%Y_%m_%d")
fh = logging.FileHandler('{:%Y-%m-%d}.log'.format(datetime.datetime.now()))
logfile = "logs/app_"+current_date+".log"
#print (logfile)
logging.basicConfig(filename=logfile,level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
LOG = logging.getLogger(__name__)


log_handler = TimedRotatingFileHandler (
            filename = logfile,
            when='midnight',
            backupCount=5
    )

log_handler.setLevel(logging.INFO)
LOG.addHandler(log_handler)
LOG.debug("******* Start Application *******")


'''date = datetime.datetime.now().strftime("%Y_%m_%d")
#print(f"log_{date}")
logfile = "logs/app_"+date+".log"
print (logfile)
fh = logging.FileHandler('email-app-{:%Y-%m-%d}.log'.format(datetime.datetime.now()))
logging.basicConfig(filename=logfile,level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
#logger.addHandler(fh)
LOG = logging.getLogger(__name__)
#LOG.app = app
'''

def create_app(config=DevelopmentConfig):
    app = Flask(__name__)
    app.app_context().push()
    
    app.config.from_object(config)

   
    
    
    # initialize extension instances
    db.init_app(app)
    db.app = app

    # migrate initialization
    migrate.init_app(app, db)
    migrate.app = app

    # login manager initialization
    #login_manager.init_app(app)
    #login_manager.app = app

    # mail initialization
    #mail.init_app(app)
    #mail.app = app

    # csrf initialization 
    csrf = CSRFProtect()
    csrf.init_app(app)
    csrf.app = app
    #app.app_context()
    #app.app_context().push()
    # register blueprints of applications
    from app.main import main as main_bp
    #app.register_blueprint(main_bp,url_prefix="/otp")
    app.register_blueprint(main_bp,url_prefix="")

    # register error blueprint
    from app.errors import errors as errors_bp
    app.register_blueprint(errors_bp)

    
    # register the authentication blueprint
    #from app.auth import auth as auth_bp
    #app.register_blueprint(auth_bp)
    return app
