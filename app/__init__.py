import os
import sys
import uuid
import datetime
import random
import math as m
#we import waitress here. 
#from waitress import serve

from flask_migrate import Migrate
from sqlalchemy import text
from flask import Flask,session,current_app 
from flask_wtf.csrf import CSRFProtect,generate_csrf
#from flask_wtf.csrf import generate_csrf
from flask_wtf.csrf import CSRFError
from config import DevelopmentConfig
from flask_ldapconn import LDAPConn

# import extensions instance
from app.models import db
from app.models import OTPModel

#from flask_mail import Mail
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

#app = ''
# instance of migrate flask
migrate = Migrate()
#mail = Mail()
#initialize log 
current_date = datetime.datetime.now().strftime("%Y_%m_%d")
#fh = logging.FileHandler('{:%Y-%m-%d}.log'.format(datetime.datetime.now()))
#uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
#logfile = "/var/log/esapp/app_"+current_date+".log"
class MyTimedRotatingFileHandler(TimedRotatingFileHandler):
    
    def rotate(self,source,destination):
        if not callable (self.rotator):
            self.new_rename(destination,source)
        else:
            self.rotator(source,destination)

    @staticmethod
    def new_rename(destination,source):
        
        print (destination)
        print (source)
        if os.path.exists(source):
            with open(destination,"w+") as fw:
                with open (source,"r+") as fr:
                    fw.write(fr.read())

            with open(source,"w+") as fw:
                fw.write ("####\n")

def logger(logPath=None, fileName=None):


    logPath = os.path.abspath(".") + "/" + logPath if logPath else os.path.abspath(".") + "/logs"
    fileName = os.path.basename(fileName).split(".")[0] if fileName else os.path.basename(__file__).split(".")[0]

    if not os.path.isdir(logPath):
        os.mkdir(logPath)

    #print(logPath)
    #print(fileName)

    

    #fileHandler = logging.FileHandler("{0}/{1}.log".format(logPath, fileName)) # this is for regular file handler
    #fileHandler = RotatingFileHandler("{0}/{1}.log".format(logPath, fileName), maxBytes=(1048576*5), backupCount=3)
    try:
    
        fileHandler = MyTimedRotatingFileHandler(filename="{0}/{1}.log".format(logPath, fileName),
                                                 when='H',
                                                 interval=12,
                                                 backupCount=0)

        
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        
        logging.getLogger("requests").setLevel (logging.WARNING)
        logging.getLogger("zeep").setLevel (logging.WARNING)
        logging.getLogger("urllib3").setLevel (logging.WARNING)
        logging.getLogger("werkzeug").setLevel (logging.ERROR)
        logging.getLogger("sqlalchemy.engine").setLevel (logging.ERROR)
        logging.getLogger("sqlalchemy.engine.Engine").setLevel (logging.ERROR)
        logging.getLogger('sqlalchemy').setLevel(logging.ERROR)
        
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG) # this is needed to get all levels, and therefore filter on each handler
        
        
        fileHandler.setFormatter(logFormatter)
        #fileHandler.setLevel(logging.DEBUG)
        fileHandler.setLevel( logging.INFO )
        
        
        logger.addHandler(fileHandler)

        

    except Exception as ex:
        logging.exception("Unhandled error\n{}".format(ex))
        raise
    finally:
        # perform an orderly shutdown by flushing and closing all handlers; called at application exit and no further use of the logging system should be made after this call.
        logging.shutdown()    
    
    return logger

#current_date = datetime.datetime.now().strftime("%Y_%m_%d")
current_date = datetime.datetime.now().strftime("%Y_%m_%d")
logfile = "service_"+current_date+""
#logfile = "service"

LOG = logger('',logfile)

LOG.debug("******* Start Application *******")




#app = create_app()
#login_manager = LoginManager(app)

config = DevelopmentConfig
app = Flask(__name__)
app.app_context().push()
app.config.from_object(config)
# initialize extension instances
db.init_app(app)
db.app = app
try:
    db.session.execute(text("SELECT 1"))
except Exception as error:
    LOG.info(error)
    pass

# migrate initialization
migrate.init_app(app, db)
migrate.app = app

login_manager = LoginManager(app)              # Setup a Flask-Login Manager
# login manager initialization
login_manager.init_app(app)
login_manager.app = app

ldap = LDAPConn(app)

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

# import and register blueprints
from flask import Blueprint

'''auth = Blueprint('auth', __name__)
main = Blueprint('main', __name__,'/main')
profile = Blueprint('profile', __name__)
tin = Blueprint('tin', __name__)
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')
'''


# import any flask extension specific to this module

# import views



from app.main.views import main as main_bp
from app.main.profile import profile as profile_bp
from app.main.tin import tin as tin_bp
from app.main.dashboard import dashboard as dashboard_bp
from app.main.auth import auth as auth_bp
from app.main.formc import formc as formc_bp
from app.main.career import career as career_bp
from app.main.swift_remittance import swift_remittance as swift_remittance_bp




#app.register_blueprint(main_bp,url_prefix="/otp")
app.register_blueprint(main_bp,url_prefix="/")
app.register_blueprint(profile_bp,url_prefix="/profile")
app.register_blueprint(tin_bp,url_prefix="/tin")
app.register_blueprint(auth_bp,url_prefix="/")
app.register_blueprint(dashboard_bp,url_prefix="/dashboard")
app.register_blueprint(formc_bp,url_prefix="/formc")
app.register_blueprint(career_bp,url_prefix="/career")
app.register_blueprint(swift_remittance_bp)

# register error blueprint
from app.errors import errors as errors_bp
app.register_blueprint(errors_bp)