import os
#import pysftp
from sqlalchemy.pool import NullPool
# set the base directory
basedir = os.path.abspath(os.path.dirname(__name__))
directory = os.getcwd()

# Create the super class
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Create the development config
class DevelopmentConfig(Config):
    SECRET_KEY ='abbl@12345'
    DEBUG = True
    #BASE_URL = "http://192.168.19.72:9443"
    #BASE_URL = "https://gw.abbl.com:24434/"
    #BASE_URL = "https://uatgw.abbl.com:9443/"
    #BASE_URL = "http://192.168.19.72:9090/"
    #BASE_URL = "http://192.168.133.131:8087/"
    BASE_URL = "https://services.abbl.com/"
    #SSL_CER_FILE = directory +'/cer/bkashuat_abbl_org.pem'
    #SQLALCHEMY_POOL_SIZE = 20   
    #SQLALCHEMY_MAX_OVERFLOW = 0
    # Flask-SQLAlchemy settings
    #SQLALCHEMY_MSSQL_DATABASE_URI = 'mssql+pyodbc://kyc:kyc123@192.168.19.72:1433/riskgradingdb?driver=SQL+SERVER'    # File-based SQL database
    #SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://sa:Abblit143@192.168.131.123:1433/riskgradingdb?driver=SQL+SERVER'    # File-based SQL database
    '''CONNECTION_SQL_STR = ("Driver={SQL Server };"
            "Server=ABTSTDEVELOP1;"
            "Database=statementportaldb;"
            "UID=stmntportal;"
            "PWD=123456;")
    
    SQL_SERVER = "192.168.19.71"
    SQLDB_USER = "stmntportal"
    SQLDB_PWD = "123456"'''

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    #MAX_CONTENT_LENGTH = 1024 * 1024
    RESUME_ALLOWED_EXTENSIONS = set(['pdf'])
    MAX_CONTENT_LENGTH = 2*1024*1024
    
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Abblit143@192.168.19.71:5432/Email_App'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    #SQLALCHEMY_ECHO = True

    SQLALCHEMY_MAX_OVERFLOW = 30
    '''SQLALCHEMY_ENGINE_OPTIONS = {

        'poolclass' : NullPool
    }'''

    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Abblit143@ABDCESTMTDB:5432/Email_App?options=-csearch_path=abbl' 
   
    SQLALCHEMY_BINDS= {
        'otp_db_bind': 'postgresql://postgres:Abblit143@ABDCESTMTDB:5432/Email_App?options=-csearch_path=abbl',
        #'bkash_db_bind': 'postgresql://bkashapidbuser:Abbl@4001@192.168.19.71:5432/mssql_schema?driver=FreeTDS'
    }

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 30,
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    SECURITY_CSRF_COOKIE_NAME = 'XSRF-TOKEN'
    WTF_CSRF_TIME_LIMIT =  5*60 #5 minutes
    
    #BKASH_API_URL    = 'http://192.168.19.71:8280/api'
    #CBS_API_URL    = 'https://bkash.abbl.com:9443/api'
    #CBS_API_USERNAME = 'abbkash'
    #CBS_API_PASSWORD = 'abbl!@Bk123'

    
    #EQCONNECTWSDL = 'http://192.168.19.166:9087/abeqws/services/EQConnect?wsdl'
    #EQENQUIRYWSDL = 'http://192.168.19.166:9087/abeqws/services/EQEnquiry?wsdl'
    #EQTRANSACTIONWSDL ='http://192.168.19.166:9087/abeqws/services/EQTransaction?wsdl'
    '''
    EQCONNECTWSDL = 'http://192.168.19.72:8443/abeqws/services/EQConnect?wsdl'
    EQENQUIRYWSDL = 'http://192.168.19.72:8443/abeqws/services/EQEnquiry?wsdl'
    EQTRANSACTIONWSDL ='http://192.168.19.72:8443/abeqws/services/EQTransaction?wsdl'
    CBS_CLIENT_APPID = 'ABEMAILAPP'
    CBS_SYSTEM = 'ABBDTSTEQ'
    #CBS_USERNAME = 'IBNWUSR'
    #CBS_PASSWORD = 'IBNWUSR'
    CBS_USERNAME = 'IBEQUSR'
    CBS_PASSWORD = 'IBEQUSR'
    CBS_UNIT = 'DEV'
    '''	
    EQCONNECTWSDL = 'http://192.168.112.154:9087/abeqws/services/EQConnect?wsdl'
    EQENQUIRYWSDL = 'http://192.168.112.154:9087/abeqws/services/EQEnquiry?wsdl'
    EQTRANSACTIONWSDL ='http://192.168.112.154:9087/abeqws/services/EQTransaction?wsdl'
    CBS_CLIENT_APPID = 'ABEMAILAPP'
    CBS_SYSTEM = 'ABBDEQ'
    #CBS_USERNAME = 'IBNWUSR'
    #CBS_PASSWORD = 'IBNWUSR'
    CBS_USERNAME = 'IBKYCUSR'
    CBS_PASSWORD = 'IBKYCUSR'
    CBS_UNIT = 'KAP'
    
    
    
    SMS_API_URL      =   'http://192.168.253.2/pushapi/dynamic/server.php'
    #SMS_API_URL     = 'http://192.168.113.108:8080/sms/'\
    OTPMSG = ''
    
    SMS_USERNAME     = 'ABBANKBKASH'
    SMS_PASSWORD     = '59A3Z82a'
    SMS_SID          = 'ABBANKBKASHOTP'
    
    '''FTP_HOST = '192.168.133.121'
    FTP_USERNAME = 'abbkash'
    FTP_PASSWORD = 'AB@bkash001'
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None
    '''
    #uid = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    API_TOKEN = 'vfviysck-mepid5xf-kywkqoim-d59wman8-bv6japky'

    url = "https://smsplus.sslwireless.com/api/v3/send-sms"

    SID = 'ABBLDISPUTE'

    #MSISDN = '8801673615816'


    MAX_OTP_LIMIT = 3
    
    OTP_EXPIRE_TIME = 2*60 #1*60

    SWIFT_SETTLEMENT_SCHEMA = 'abbl'
    SWIFT_SETTLEMENT_TABLE = 'settlement_data'
    SWIFT_LINK_EXPIRY_SECONDS = 15 * 60
    SWIFT_OTP_EXPIRY_SECONDS = 5 * 60
    SWIFT_UPLOAD_FOLDER = os.path.join(directory, 'app', 'static', 'uploads', 'swift_remittance')

    
    USER_ENABLE_EMAIL= False
    
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')

    LDAP_SERVER = 'LDAP://abdcad1.abbl.org'
    LDAP_PORT = 389
    LDAP_BINDDN = 'cn=admin,dc=abbl,dc=org'
    LDAP_SECRET  = 'forty-two'
    LDAP_CONNECT_TIMEOUT  = 10  # Honored when the TCP connection is being established
    LDAP_USE_TLS  = False

    

    


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
