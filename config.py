import os
from sqlalchemy.pool import NullPool
# set the base directory
basedir = os.path.abspath(os.path.dirname(__name__))
directory = os.getcwd()

# Create the super class
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Create the development config
class DevelopmentConfig(Config):
    SECRET_KEY ='abbl@12345'
    DEBUG = True
    #BASE_URL = "http://192.168.19.72:9443"
    #BASE_URL = "https://gw.abbl.com:24434/"
    #BASE_URL = "https://uatgw.abbl.com:9443/"
    BASE_URL = "http://192.168.19.72:9090/"
    #SSL_CER_FILE = directory +'/cer/bkashuat_abbl_org.pem'
    #SQLALCHEMY_POOL_SIZE = 20   
    #SQLALCHEMY_MAX_OVERFLOW = 0
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Abblit143@192.168.19.71:5432/Email_App'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    '''SQLALCHEMY_ENGINE_OPTIONS = {

        'poolclass' : NullPool
    }'''

    SQLALCHEMY_BINDS= {
        'otp_db_bind': 'postgresql://postgres:Abblit143@192.168.19.71:5432/Email_App',
        #'bkash_db_bind': 'postgresql://bkashapidbuser:Abbl@4001@192.168.19.71:5432/mssql_schema?driver=FreeTDS'
    }
    
    SECURITY_CSRF_COOKIE_NAME = 'XSRF-TOKEN'
    WTF_CSRF_TIME_LIMIT =  5*60 #5 minutes
    
    #BKASH_API_URL    = 'http://192.168.19.71:8280/api'
    #CBS_API_URL    = 'https://bkash.abbl.com:9443/api'
    #CBS_API_USERNAME = 'abbkash'
    #CBS_API_PASSWORD = 'abbl!@Bk123'

    
    EQCONNECTWSDL = 'http://192.168.19.166:9087/abeqws/services/EQConnect?wsdl'
    EQENQUIRYWSDL = 'http://192.168.19.166:9087/abeqws/services/EQEnquiry?wsdl'
    EQTRANSACTIONWSDL ='http://192.168.19.166:9087/abeqws/services/EQTransaction?wsdl'

    
    
    
    CBS_CLIENT_APPID = 'ABEMAILAPP'
    CBS_SYSTEM = 'ABBDTSTEQ'
    CBS_USERNAME = 'IBNWUSR'
    CBS_PASSWORD = 'IBNWUSR'
    CBS_UNIT = 'DEV'
    
    
    SMS_API_URL      =   'http://192.168.253.2/pushapi/dynamic/server.php'
    #SMS_API_URL     = 'http://192.168.113.108:8080/sms/'\
    OTPMSG = ''
    
    SMS_USERNAME     = 'ABBANKBKASH'
    SMS_PASSWORD     = '59A3Z82a'
    SMS_SID          = 'ABBANKBKASHOTP'

    #uid = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    API_TOKEN = 'vfviysck-mepid5xf-kywkqoim-d59wman8-bv6japky'

    url = "https://smsplus.sslwireless.com/api/v3/send-sms"

    SID = 'ABBLDISPUTE'

    #MSISDN = '8801673615816'


    MAX_OTP_LIMIT = 3
    
    OTP_EXPIRE_TIME = 2*60 #1*60

    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')

    


# Create the testing config
class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test-data.db')
    #SQLALCHEMY_TRACK_MODIFICATIONS = False

# create the production config
class ProductionConfig(Config):
    DEBUG = False
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    #SQLALCHEMY_TRACK_MODIFICATIONS = False