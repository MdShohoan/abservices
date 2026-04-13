from app import app,db
import urllib
import datetime
from pprint import pprint
import logging
import ldap3
import json

from app.main import auth
from flask import Blueprint, render_template,render_template_string,request, url_for, flash, redirect, session,Blueprint,g

from flask_user import roles_required, UserManager, UserMixin
from flask_login import LoginManager, login_required, logout_user, login_user, current_user


from flask_ldap3_login import AuthenticationResponse,AuthenticationResponseStatus
from flask_ldap3_login import LDAP3LoginManager

from flask_ldapconn import LDAPConn

from werkzeug.exceptions import abort
#from flask_sqlalchemy import SQLAlchemy
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO
from app.dbmodels.user import User,UserRoles,Role



login_manager = LoginManager(app)              # Setup a Flask-Login Manager

#login_manager.init_app(app)
#login_manager.app = app

# Create a dictionary to store the users in when they authenticate
# This example stores users in memory.
users = {}

'''app.config['LDAP_SERVER'] = 'LDAP://abdcad1.abbl.org'
app.config['LDAP_PORT'] = 389
app.config['LDAP_BINDDN'] = 'cn=admin,dc=abbl,dc=org'
app.config['LDAP_SECRET']  = 'forty-two'
app.config['LDAP_CONNECT_TIMEOUT']  = 10  # Honored when the TCP connection is being established
app.config['LDAP_USE_TLS']  = False'''



#LDAP_USE_TLS = True  # default
#LDAP_REQUIRE_CERT = ssl.CERT_NONE  # default: CERT_REQUIRED
#LDAP_TLS_VERSION = ssl.PROTOCOL_TLSv1_2  # default: PROTOCOL_TLSv1
#LDAP_CERT_PATH = '/etc/openldap/certs'

ldap = LDAPConn(app)

auth = Blueprint('auth', __name__)

# Declare a User Loader for Flask-Login.
# Simply returns the User if it exists in our 'database', otherwise
# returns None.
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(user_id)
    except:
        return None


@auth.before_request
def get_current_user():
    g.user = current_user


@auth.route('/')
def home_page():
    """The home page."""
    print ('home page')
    #return render_template('home.html')
    # print(conn)
    #if current_user.is_authenticated:
            #return redirect(url_for('dashboard.index'))
        
    return redirect(url_for('auth.login'))
    


@auth.route('/home')
def index():
    try:
        
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        else : 
            return redirect(url_for('auth.login'))
        
        #return redirect(url_for('auth.login'))
        #return redirect(url_for('dashboard.index'))
        #tasks = []
        #conn = get_db_connection()
        #tasks = conn.execute('SELECT * FROM abblitincidentinfo').fetchall()
        #print ("hello world ")
        #print (' Home Index ')
        #print (current_user.email)
        #tasks = session.query(Task).all()
        #tasks = Task.query.all()
        #print(tasks)
        #conn.close()

    except Exception as e:
        print(e)
    finally:
        return render_template('index.html')
        #return redirect(url_for('auth.login'))




@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        #flash('You are already logged in.')
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #username = request.form.get('username')
        #password = request.form.get('password')
        dn = '@abbl.org'
        username = request.form['username'] 
        password = request.form['password']

        print (username)
        print (password)

        
        status, result, response =  User.try_login(username + dn, password)
        print (status, result)
        
        if not status :
            #flash('Invalid username or password. Please try again.', 'danger')
            return render_template('accounts/login.html')

        dbresults = User.query.all()
        print (dbresults)
        print ("Username : " + username)
        user = User.query.filter_by(Username=username).first()
        print ("user result all  : ")
        print (user)
        role_name = user.user_role
        
        #print (user.id)

        #if not user:
            #user = User(username, password)
            #db.session.add(user)
            #db.session.commit()
        login_user(user)
        #flash('Dashboard.', 'success')
        return redirect(url_for('dashboard.index'))
        '''if "formc" in role_name:
            return redirect(url_for('dashboard.indexformc'))
        else:
            return redirect(url_for('dashboard.index'))
        '''
        #return redirect(url_for('dashboard.index'))

    #else:
        #flash(form.errors, 'danger')

    return render_template('accounts/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/allusers')
@login_required
def allusers():
    #user = User.query.all()
    userslist = User.query\
            .join(UserRoles,User.id ==UserRoles.user_id).\
             add_columns(User.id,User.Username,User.Displayname,User.Branch,User.Department,User.Phone,User.email,Role.name).join(Role,Role.id ==UserRoles.role_id).all() 
            
    #userlists = []
    for result in userslist:
        print (result)
    print (userslist)
    return render_template('accounts/userslist.html',userslist= userslist)
    
@auth.route('/checkuser',methods=['POST'])
def checkuser():
    print (' check user...')
    
    dn = '@abbl.org'
    username = request.form['username'] 
    password = request.form['password']
    domainname = request.form['domainid']
    status, result, response =  User.searchUser(username + dn, password,domainname)
    
    
    #print (status, result)
    #User.searchUser('saidur')
    '''ldapc = ldap.connection
    basedn = 'ou=people,dc=abbl,dc=com'
    search_filter = '(objectClass=posixAccount)'
    attributes = ['sn', 'givenName', 'uid', 'mail']
    ldapc.search(basedn, search_filter, ldap3.SUBTREE,
                 attributes=attributes)
    response = ldapc.response
    print (response)
    return render_template_string('test')'''
    #return render_template_string('accounts/adduser.html')
    return json.dumps({'status':'OK','status':status,'result':result,'response':response});


@auth.route('/adduser',methods=['GET','POST'])
@login_required
def adduser():
    
    if request.method == 'POST':

        Username = request.form['Username'].strip() 
        Displayname = request.form['Displayname'].strip()
        Office = 'AB'
        Department = 'AB'
        Branch = request.form['sBranch'].strip()
        Email = request.form['sEmail'].strip()
        Phone = request.form['sMobile'].strip()
        application_list = request.form.getlist('user_role')
        #User_Role = request.form['user_role'].strip()
        # Convert to comma delimited string
        User_Role = ','.join(application_list)
        
        print ('User Role : *****************')
        print (User_Role)
        
        #User_Role = request.form['user_role'].strip()
        #User_Role = ''
        Designation = 'AB'
        password ='ab'
        role_id = request.form['role'].strip()
        if not User.query.filter(User.Username == Username).first():
            #domainname = request.form['domainid']

            print ('Display Name : ')
            print (Displayname)
            dt =  datetime.datetime.now()
            id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            user = User(
                id = id,
                Username = Username,
                Displayname=Displayname,
                Office=Office,
                Department=Department,
                Branch=Branch,
                Phone=Phone,
                Email=Email,
                password=password,
                Designation=Designation,
                is_active = True,
                user_role = User_Role
            
            )
            print (user)
            #user.roles.append(Role(name=role))
            db.session.add(user)
            db.session.commit()
            print (user.id)
            dt =  datetime.datetime.now()
            id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            user_role = UserRoles(id=id,user_id=user.id, role_id=role_id)
            db.session.add(user_role)
           
            db.session.commit()
            print ('Add user')
            flash ('Successfully add User ','success')
            return redirect('/allusers')
        else :
            flash ('User already exists','success') 
            return redirect('/adduser')
    else : 

    
        #print (' add user...')
        #User.searchUser('saidur')
        '''ldapc = ldap.connection
        basedn = 'ou=people,dc=abbl,dc=com'
        search_filter = '(objectClass=posixAccount)'
        attributes = ['sn', 'givenName', 'uid', 'mail']
        ldapc.search(basedn, search_filter, ldap3.SUBTREE,
                    attributes=attributes)
        response = ldapc.response
        print (response)
        return render_template_string('test')'''
        #user = User.query.filter_by(Username = current_user.Username ).first()
        #userslist = User.query\
                #.join(UserRoles,User.id ==UserRoles.user_id).\
                #add_columns(User.id,User.Username,User.Displayname,User.Branch,User.Department,User.Phone,User.email,Role.name).join(Role,Role.id ==UserRoles.role_id).all() 

    roles  = Role.query.all()
    #print (roles)
    user = {}
    cur_role_id = ''

    return render_template('accounts/user.html',roles = roles,user=user,cur_role_id =cur_role_id)

@auth.route('/edituser/<string:id>',methods=['GET','POST'])
def edituser(id):

    if request.method == 'POST':

        user = User.query.filter_by(id = id ).first()
        print (id)
        print (user)
        
        if user:
            user.Username = request.form['Username'].strip() 
            user.Displayname = request.form['Displayname'].strip() 
            user.Office = 'AB'
            user.Department = 'AB'
            user.Branch = request.form['sBranch'].strip()
            user.email = request.form['sEmail'].strip()
            user.Phone = request.form['sMobile'].strip()
            print ('Application ....')
            application_list = request.form.getlist('user_role')
            User_Role = ','.join(application_list)
            print (User_Role)
            user.user_role = User_Role
            user.Designation = 'AB'
            user.password ='ab'

            db.session.commit()
            
            
            
            user_role = UserRoles.query.filter_by(user_id = id ).first()
            user_role.role_id = request.form['role']
            db.session.commit()

            #flash ('Updated User Record Successfully','success')
            return redirect('/allusers')


        
        return render_template_string('edit...')

    else:

        user = User.query.filter_by(id = id ).first()
        user_role = UserRoles.query.filter_by(user_id = id ).first()
        #user_role = UserRoles(user_id=user.id, role_id=role_id)
        print (user)
        print (user_role.role_id)
        roles  = Role.query.all()
        return render_template('accounts/user.html',roles = roles,user=user,cur_role_id =user_role.role_id )
    
    #return render_template_string ('hello world ')

@auth.errorhandler(404)
def not_found(error):
    print ("error 404")
    return render_template('error.html'), 404

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@auth.errorhandler(403)
def access_forbidden(error):
    return render_template('page-403.html'), 403

@auth.errorhandler(404)
def not_found_error(error):
    print ('Not found..')
    return render_template('page-404.html'), 404

@auth.errorhandler(500)
def internal_error(error):
    return render_template('page-500.html'), 500

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('page-403.html'), 403

@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template('page-413.html'), 403