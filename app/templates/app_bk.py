import os
#from datetime import timedelta
from datetime import timedelta
from time import gmtime, strftime


from flask import Flask, jsonify, make_response, request,Blueprint
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from flask_restx import Api
#from flask_jwt_extended import JWTManager,create_access_token

from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
#from flask_jwt_extended import get_jwt_identity
#from flask_jwt_extended import jwt_required


from flask_jwt_extended import get_jwt
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import set_access_cookies
from flask_jwt_extended import unset_jwt_cookies
#from flask_jwt_extended import create_access_token
import json
import uuid
import jwt
import datetime

#api_bp = Blueprint("api", __name__, url_prefix="/api")
#authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

'''api = Api(
    api_bp,
    version="1.0",
    title="Flask API with JWT-Based Authentication",
    description="Welcome to the Swagger UI documentation site!",
    doc="/ui",
    authorizations=authorizations,
)'''

#app = Flask(__name__)
app = Flask(__name__, template_folder="templates")
 
app.config['SECRET_KEY']='9c32c6a0c719a0ca815bc1b16f71fce1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your code!

#app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["TOKEN_EXPIRE_HOURS"]        = 0
app.config["TOKEN_EXPIRE_MINUTES"]      = 15
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
app.config["TESTING"] = timedelta(hours=1)
 
#db = SQLAlchemy(app)

#app.register_blueprint(api_bp)

jwt = JWTManager(app)

# Using an `after_request` callback, we refresh any token that is within 30
# minutes of expiring. Change the timedeltas to match the needs of your application.
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response



def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']
 
       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
           current_user = Users.query.filter_by(public_id=data['public_id']).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(current_user, *args, **kwargs)
   return decorator

@app.route('/mytoken', methods=['POST'])
def signup_user(): 
    data = request.get_json() 
    
    grant_type = data['grant_type']
    username   = data['username']
    password =  data['password']
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = Users(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user) 
    db.session.commit()   
    return jsonify({'message': 'registered successfully'})

@app.route("/api/token", methods=["POST"])
def create_token():
    #username = request.json.get("username", 'saidur')
    #password = request.json.get("password", '1234')
    # Query your database for username and password
    #user = User.query.filter_by(username=username, password=password).first()
    #user  = { "id" : "1"}
    #user.id = 1 

    x =  '{ "id":"1", "username":"saidur", "password":"123457"}'
    user = json.loads(x)

    print (user['id'])

    data = request.get_json()
    print (data)
    grant_type = data['grant_type']
    username   = data['username']
    password =  data['password']
    
    
    user = 'saidur'
    id = 1
    if user is None:
        # the user was not found on the database
        return jsonify({"msg": "Bad username or password"}), 401
    
    # create a new token with the user id inside
    #access_token = create_access_token(identity=id)
    access_token = create_access_token(identity="example_user")
    refresh_token = create_refresh_token(identity="example_user")
    #exp_timestamp = get_jwt()["exp"]
    now = datetime.datetime.now(datetime.timezone.utc)
    expire_sec= _get_token_expire_time()
    target_timestamp =(now + timedelta(seconds=expire_sec))
    issued_date = now.strftime("%A, %d %B %Y %H:%M:%S")
    expired_date = target_timestamp.strftime("%A, %d %B %Y %H:%M:%S") 
    
    
    print (now)
    print(now.strftime("%A"))
    print(now.strftime("%A, %d %B %Y %H:%M:%S"))
    print(target_timestamp.strftime("%A, %d %B %Y %H:%M:%S"))
    
    print("Your Time Zone is GMT", strftime("%z", gmtime()))

    response = {
                "access_token": access_token,
                "token_type" : "bearer",
                "expires_in": _get_token_expire_time(),
                "client_id" : "ACS",
                "refresh_token" : refresh_token,
                "username" : username,
                "issued" : issued_date,
                "expires" :expired_date,
                "responsecode" : 0
    
            }
    
    
    
    
    return jsonify(response)

def _get_token_expire_time():
    #token_age_h = app.config.get("TOKEN_EXPIRE_HOURS")
    #token_age_m = app.config.get("TOKEN_EXPIRE_MINUTES")
    token_age_h = 0
    token_age_m = 15
    expires_in_seconds = token_age_h * 3600 + token_age_m * 60
    print (expires_in_seconds)
    #return expires_in_seconds if not app.config["TESTING"] else 5
    return expires_in_seconds


@app.route("/api/ACSAPIService/InitiatePayment", methods=["GET"])
def InitiatePayment():

    transaction_id = uuid.uuid4()

    response = {
                "transaction_id": transaction_id,
                "response_code" : "0",
                "response_url": "http://uatabbank.com/acs/retail/",
               
                }

    return jsonify(response)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  