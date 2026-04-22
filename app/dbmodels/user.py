from app import app,db
import ldap3
import json

#from app import create_app
#from app import current_app
#from run import create_app
#from app import db

#from app.models import db

#from app import db,UserManager,UserMixin
#from flask_login import LoginManager, login_required, logout_user, login_user, current_user
from flask_user import roles_required, UserManager, UserMixin,current_user



def get_ldap_connection():
    #conn = ldap.initialize(app.config['LDAP_PROVIDER_URL'])
    ldapserver = 'LDAP://abdcad1.abbl.org'
    server = ldap3.Server(ldapserver)
    return server


# UserRole = db.Table(
#     'user_roles', db.Model.metadata,
#     db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
#     db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
#     bind_key='otp_db_bind',
#     schema='abbl'
# )

UserRole = db.Table(
    'user_roles',
    db.Model.metadata,
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('user_id', db.Integer, db.ForeignKey('abbl.users.id', ondelete='CASCADE')),
    db.Column('role_id', db.Integer, db.ForeignKey('abbl.roles.id', ondelete='CASCADE')),
    schema='abbl',
)
class User(db.Model,UserMixin):
        __tablename__ = 'users'
        #__table_args__ = {"schema":"abbl"}
        __table_args__ = {'schema': 'abbl'}   # ✅ ADD THIS
        #__bind_key__ = 'otp_db_bind'
        id = db.Column(db.Integer, primary_key=True)
        is_active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
        
        Username = db.Column(db.String(20), nullable=False, unique=True)
        Displayname = db.Column(db.String(200), nullable=True,unique=False)
        Office = db.Column(db.String(4), nullable=True,unique=False)
        Department = db.Column(db.String(25), nullable=True,unique=False)
        Branch = db.Column(db.String(4), nullable=True,unique=False)
        Phone = db.Column(db.String(25), nullable=True,unique=False)
        
        
        # User authentication information. The collation='NOCASE' is required
        # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
        email = db.Column(db.String(255), nullable=False, unique=True)
        #created_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=True, server_default='ab')
        user_role = db.Column(db.String(255), nullable=True,unique=False)
        # User information
        #first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        #last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

        # Define the relationship to Role via UserRoles
        #roles = db.relationship('Role', secondary='user_roles',primaryjoin="user_roles.user_id==users.id",secondaryjoin="user_roles.role_id==roles.id")
        roles = db.relationship('Role',secondary=UserRole)
        

        def __init__(self,id, Username, password, Displayname,Office, Department,Branch,Phone,Email,Designation,is_active,user_role ):
            #self.id = id
            #self.is_active         = 1
            self.id                 = id 
            self.Username           = Username
            self.Displayname        = Displayname
            self.Office             = Office
            self.Phone              = Phone
            self.email              = Email 
            self.password           = 'ab'
            self.Designation        =''
            self.Branch             = Branch
            self.user_role          = user_role
            

        
        
        @staticmethod
        def searchUser(username, password,searchUsername):
            status = False
            result = ''
            response = ''
            server = get_ldap_connection()
            conn = ldap3.Connection(server, user=username, password=password)
            
            #searchUsername = 'pikul'
            if conn.bind():
                
                conn.search('DC=abbl,DC=org','(&(objectclass=user)(sAMAccountName='+searchUsername+'))',attributes='*')
                #conn.search(search_base='dc=abbl,dc=org',search_filter=sids,attributes=['objectsid', 'sAMAccountName'])
                #conn.search('DC=abbl,DC=org','(&(objectclass=user)(sAMAccountName='+username+'))', attributes=['memberOf'])
                #conn.search('DC=abbl,DC=org','(&(objectclass=user)(sAMAccountName='+username+'))', attributes=['memberOf'])
                #print (conn.response)
                #username = 'pikul'
                #conn.search(search_base='DC=abbl,DC=org', search_filter='(&(objectClass=user)(userPrincipalName='+username+'))', search_scope='SUBTREE', attributes='*')
                #conn.search('DC=abbl,DC=org','(&(objectclass=user)(sAMAccountName=saidur))')
                
                #print (conn.response)

                #print (conn.entries[0])
                #entry = conn.entries[0]
                #print(entry.entry_to_json())

                #response = json.loads(entry.entry_to_json())

                #print (response['attributes'])

                #attributes = response['attributes']
                #displayName = attributes['displayName']
                #print (displayName)
                #dn = response['dn']
                #print (' Raw DN ')
                #print (response['dn'])
                #letter_list = a_string.split(",")
                #print (conn.response[0]['raw_dn'])

                #raw_dn = conn.response[0]['raw_dn']
                results = {}

                attrs   = conn.response[0]['attributes']
                #print (attrs)
                results['serachusername'] = attrs['cn']
                results['email'] = attrs['userPrincipalName']
                results['department'] = attrs['department']
                results['office'] = attrs['physicalDeliveryOfficeName']
                results['mobile'] = attrs['mobile']
                results['givenName'] = attrs['givenName']

                #print (results)


                #print (attrs['userPrincipalName'])
                #print ('Department ')
                #print (attrs['department'])

                #print ('Physical Office Name')
                #print (attrs['physicalDeliveryOfficeName'])

                #print ('mobile')
                #print (attrs['mobile'])
                
                #print(attrs['displayName'])
                #for memb in attrs['memberOf']:
                    #print(memb.partition('=')[2].partition(',')[0])
                
                #status, result, response, _ = conn.
                #status, result, response, _ = conn.search('o=test', '(objectclass=*)')  #
                #status, result, response, _ = conn.search(search_base='DC=abbl,DC=org',search_filter = '(&(objectClass=user)(userPrincipalName=' + username + '))',search_scope = 'SUBTREE',attributes = '*')
                #print ('...Status ... ')
                #print (status)
                #basedn = 'ou=people,dc=abbl,dc=com'
                #search_filter = '(objectClass=posixAccount)'
                #attributes = ['sn', 'saidur', 'uid', 'mail']
                #conn.search(basedn, search_filter, ldap3.SUBTREE,attributes=attributes)
                #response = conn.response
                #conn.search('DC=abbl,DC=com','(&(objectclass=user)(sAMAccountName=saidur))')

                #print (response)
                #status, result, response, _ = conn.search('o=test', '(objectclass=*)')
                #conn.simple_bind_s(
                    #'cn=%s,ou=Users,dc=testathon,dc=net' % username, password
                #)
                status = True
                result = results
                response ='found'
            else : 
                status = False
                result = ''
                response ='Invalid Login Credentials'

            return status, result, response
        
        
        @staticmethod
        def try_login(username, password):
            
            #status, result, response = ''
            
            status = False
            result = ''
            response = ''
            server = get_ldap_connection()
            conn = ldap3.Connection(server, user=username, password=password)
            
            if conn.bind():
                #status, result, response, _ = conn.
                #status, result, response, _ = conn.search('o=test', '(objectclass=*)')  #
                #status, result, response, _ = conn.search(search_base='DC=abbl,DC=org',search_filter = '(&(objectClass=user)(userPrincipalName=' + username + '))',search_scope = 'SUBTREE',attributes = '*')
                #print ('...Status ... ')
                #print (status)
                #status, result, response, _ = conn.search('o=test', '(objectclass=*)')
                #conn.simple_bind_s(
                    #'cn=%s,ou=Users,dc=testathon,dc=net' % username, password
                #)
                status = True
                result = ''
                response =''
                
            return status, result, response
            
        def is_authenticated(self):
            return True

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def get_id(self):
            return self.id

        
        
        def get_my_role(user_id):
                #UserRoles.query.filter
                #user_id = 6
                #user_role =UserRoles.query.filter(user_id == id).first()
                #print ("user role...")
                #role_name = self.get_role(user_role.role_id)
                print ("User ID : ")
                print (user_id)
                user_role = UserRoles.query.filter(user_id == user_id).first() 
                #role =Role.query.filter(id == user_role.role_id).first()
                print ("User role id")
                print (user_role.role_id)
                #role =Role.query.filter(id == 1).first()
                role_name = User.get_role (user_role.role_id)
                print ("Role Name")
                print (role_name)
                return role_name
                
                 
                #query_user_role = User.query.join(user_roles).join(Role).filter((roles.c.user_id == User.id) & (roles_users.c.role_id == Role.id)).all()
                #print (query_user_role)
                #return query_user_role 

        
        def get_role (id):
            print ("Role id : ")
            print (id)
            role =Role.query.filter(id == id).first()
            print (role)
            return role.name
        
        def has_role(self):
            user =UserRoles.query.filter(id == self.id).first()
            return True
            #return self.access == 'Admin'

user_manager = UserManager(app, db, User)

# Define the Role data-model
class Role(db.Model):
        __tablename__ = 'roles'
        __table_args__ = {"schema":"abbl"}
        #__bind_key__ = 'otp_db_bind'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), unique=True)

# ORM handle for the same physical table as UserRole (must not redefine the table in MetaData)
class UserRoles(db.Model):
    __table__ = UserRole

    


db.create_all()
# Create 'member@example.com' user with no roles
