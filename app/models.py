from flask_sqlalchemy import SQLAlchemy
from requests.models import RequestField

db = SQLAlchemy()
#db = SQLAlchemy(session_options={'autocommit':True})


class EQSessiontoken(db.Model):

	__tablename__ = 'eqsessiontoken'
	id = db.Column('id', db.BigInteger, primary_key = True)
	eqsessiontoken  = db.Column('eqsessiontoken',db.Text, nullable=False)
	#eqsessiontoken  = db.Column(db.String(100), nullable=True)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	def __init__(self,id,eqsessiontoken,created_at):
		
		self.id = id
		self.eqsessiontoken =eqsessiontoken
		self.created_at = created_at


class OTPModel(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "otpinfo"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)
	#id = db.Column(db.Integer, primary_key=True)
	mobile = db.Column(db.String(13), unique=True, nullable=False)
	email = db.Column("email",db.String(55),  nullable=False)
	code = db.Column("code",db.String(120) , nullable=False)
	api_token = db.Column("api_token",db.Text , nullable=False)
	api_key = db.Column("api_key",db.Text , nullable=False)
	#code = db.Column("code",db.String(120) , nullable=False)
	
	otp_tries = db.Column("otp_tries", db.Integer)
	status = db.Column("status", db.Integer,nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	otp_request_count = db.Column("otp_request_count", db.Integer)

	

	def __init__(self, id, mobile,email,code,api_token,api_key,otp_tries,status,created_at,otp_request_count):
		self.id = id
		self.mobile = mobile
		self.email = email
		self.code = code
		self.api_token = api_token
		self.api_key = api_key
		
		self.otp_tries = otp_tries
		self.status = status
		self.created_at = created_at
		self.otp_request_count = otp_request_count

	def __repr__(self):
		return f"<Item {self.email}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "mobile": self.mobile,   
				 "email": self.email, 
				 "code":self.code,
				 "api_token" : self.api_token,
				 "api_key" : self.api_key,
				 
				 "otp_tries" : self.otp_tries,
				 "status" : self.status,
				 "created_at" :self.created_at,
				 "otp_request_count":self.otp_request_count
				}


class SMSINFO(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "sms_info"
	__table_args__ = {"schema":"abbl"}
	__bind_key__ = 'otp_db_bind'

   
	id = db.Column("id", db.BIGINT,primary_key=True)
	
	#id = db.Column(db.Integer, primary_key=True)
	#message = db.column ("message",db.Text, nullable=True)
	message = db.Column("message",db.Text , nullable=False)
	mobile = db.Column("mobile",db.String(15) , nullable=False)
	#message = db.Column(db.String(13), unique=True, nullable=False)
	sms_send_time = db.Column("sms_send_time",db.DATETIME,  nullable=False)
	#ssl_reply_message = db.column ("ssl_reply_message",db.Text)
	ssl_reply_message = db.Column("ssl_reply_message",db.Text , nullable=True)
	#ssl_sms_reply_status = db.column ("ssl_sms_reply_status",db.Text)
	ssl_sms_reply_status = db.Column("ssl_sms_reply_status",db.Text , nullable=True)
	status = db.Column("status",db.Integer,nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	trackingcode = db.Column("trackingcode",db.Text , nullable=False)
	code = db.Column("code",db.String(6) , nullable=False)
	callback_url = db.Column("callback_url",db.Text , nullable=True)
	
	
	#code = db.Column("code",db.String(120) , nullable=False)
	#api_token = db.Column("api_token",db.String(6) , nullable=False)
	#api_key = db.Column("api_key",db.Text , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#status = db.Column("status", db.Integer,nullable=False)
	#created_at = db.Column("created_at",db.DATETIME , nullable=False)

	def __init__(self,id,code,mobile,message,status,sms_send_time,ssl_reply_message,ssl_sms_reply_status,created_at,trackingcode,callback_url):
		
		self.id = id
		self.code   = code 
		self.mobile = mobile
		self.message = message
		self.status = status
		self.sms_send_time = sms_send_time
		self.ssl_reply_message = ssl_reply_message
		self.ssl_reply_status = ssl_sms_reply_status
		self.created_at = created_at
		self.trackingcode = trackingcode
		self.callback_url = callback_url

	def __repr__(self):
		return f"<Item {self.mobile}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "code": self.code,   
				 "mobile": self.mobile,   
				 "message": self.message, 
				 "sms_send_time":self.sms_send_time,

				 "ssl_reply_message" : self.ssl_reply_message,
				 "ssl_reply_status" : self.ssl_sms_reply_status,
				 
				 "status" : self.status,
				 "created_at" :self.created_at,
				 "trackingcode":self.trackingcode,
				 "callback_url" : self.callback_url
				}

class CBS_CUSTOMERS(db.Model):
		
		__tablename__ = "cbs_customers"
		__table_args__ = {"schema":"abbl"}
		#__bind_key__ = 'otp_db_bind'
		#__bind_key__ = 'cbs_db_bind'

		id = db.Column("id", db.BIGINT,primary_key=True)
		basicNumber = db.Column("basicNumber",db.String(6), nullable=True)
		businessPhone = db.Column("businessPhone",db.String(15), nullable=True)
		customerName = db.Column("customerName",db.Text, nullable=True)
		customerType  = db.Column("customerType",db.String(10), nullable=True)
		customerTypeDesc = db.Column("customerTypeDesc",db.String(25), nullable=True)
		dateOfBirth = db.Column("dateOfBirth",db.String(22), nullable=True)
		defaultBranch = db.Column("defaultBranch",db.String(6), nullable=True)
		email1 = db.Column("email1",db.String(50), nullable=True)
		email2 = db.Column("email2",db.String(50), nullable=True)
		homePhone = db.Column("homePhone",db.String(25), nullable=True)
		idDocCode = db.Column("idDocCode",db.String(500), nullable=True)
		idExpiryDate = db.Column("idExpiryDate",db.String(20), nullable=True)
		#idExpiryDate = db.Column("idExpiryDate",db.String(20), nullable=True)
		mobile = db.Column("mobile",db.String(20), nullable=True)
		residenceCountry  = db.Column("residenceCountry",db.String(2), nullable=True)
		status = db.Column("status",db.Integer, nullable=False)
		taxid = db.Column("taxid",db.String(80), nullable=False)
		created_at = db.Column("created_at",db.DATETIME , nullable=False)
		csrf = db.Column("csrf",db.String(12), nullable=False)
		requestid = db.Column("requestid",db.String(12), nullable=False)

		def __init__(self, id, basicNumber,businessPhone,customerName,customerType,customerTypeDesc,dateOfBirth,email1,email2,homePhone,idDocCode,idExpiryDate,
		mobile,residenceCountry,status,taxid,created_at,requestid,csrf):
			
			self.id = id
			self.basicNumber = basicNumber
			self.businessPhone = businessPhone
			self.customerName = customerName
			self.customerType = customerType
			self.customerTypeDesc = customerTypeDesc
			self.dateOfBirth = dateOfBirth
			self.email1 = email1
			self.email2 = email2
			self.idDocCode = idDocCode
			self.idExpiryDate = idExpiryDate
			self.mobile = mobile
			self.residenceCountry = residenceCountry
			self.status = status
			self.taxid = taxid
			self.created_at = created_at
			self.requestid  = requestid
			self.csrf  = csrf          
			#self.user_otp = user_otp
		
		def __repr__(self):
			return f"<id {self.id}>"
		
		
		@property
		def serialize(self):
			"""
			Return item in serializeable format
			"""
			return { 
					"id" : self.id,
					"basicNumber" : self.basicNumber,
					"businessPhone" : self.businessPhone,
					"customerName" : self.customerName,
					"customerType" : self.customerType,
					"customerTypeDesc" : self.customerTypeDesc,
					"dateOfBirth" : self.dateOfBirth,
					"email1" : self.email1,
					"email2" : self.email2,
					"idDocCode" : self.idDocCode,
					"mobile"       : self.mobile,
					"idExpiryDate": self.idExpiryDateile,   
					"residenceCountry":self.residenceCountry,
					"status":self.status,
					"api_token" : self.taxid,
					"created_at" :self.created_at,
					"taxid" : self.taxid,
					"requestid" : self.requestid,
					"csrf" : self.csrf
					}





class OTP_HISTORY(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "otp_history"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)
	#id = db.Column(db.Integer, primary_key=True)
	mobile = db.Column(db.String(13), unique=True, nullable=False)
	api_token = db.Column("api_token",db.String(6) , nullable=False)
	code = db.Column("code",db.String(120) , nullable=False)
	user_otp = db.Column("user_otp",db.String(120) , nullable=False)
	
	#api_key = db.Column("api_key",db.Text , nullable=False)
	#code = db.Column("code",db.String(120) , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#status = db.Column("status", db.Integer,nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)

	def __init__(self, id, mobile,api_token,code,user_otp,created_at):
		self.id = id
		self.mobile = mobile
		self.api_token = api_token
		self.code = code
		self.user_otp = user_otp
		self.created_at = created_at

	def __repr__(self):
		return f"<Item {self.email}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "mobile": self.mobile,   
				 "code":self.code,
				 "user_otp":self.user_otp,
				 "api_token" : self.api_token,
				 "created_at" :self.created_at
				}


class CUSTINFO(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "custinfo"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)
	#id = db.Column(db.Integer, primary_key=True)
	account_no = db.Column("account_no",db.String(15), nullable=False)
	customer_name = db.Column("customer_name",db.String(255), nullable=False)
	mobile = db.Column(db.String(13), nullable=False)
	email = db.Column(db.String(155), nullable=False)
	code = db.Column("code",db.String(120) , nullable=False)
	api_token = db.Column("api_token",db.String(6) , nullable=False)
	api_key = db.Column("api_key",db.Text , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#user_otp = db.Column("user_otp",db.String(120) , nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	sms_verify_status = db.Column("sms_verify_status", db.Integer,nullable=False)
	email_verify_status = db.Column("email_verify_status", db.Integer,nullable=False)
	status = db.Column("status", db.Integer,nullable=False)
	statement_path = db.Column("statement_path",db.String(500) , nullable=False)
	branch_code = db.Column("branch_code",db.String(6) , nullable=False)
	internal_account = db.Column("internal_account",db.String(20) , nullable=False)
	external_account = db.Column("external_account",db.String(20) , nullable=False)
	#api_key = db.Column("api_key",db.Text , nullable=False)
	#code = db.Column("code",db.String(120) , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#status = db.Column("status", db.Integer,nullable=False)
	

	def __init__(self,id,account_no,customer_name,mobile,email,code,api_token,api_key,created_at,sms_verify_status,email_verify_status,status,statement_path,branch_code,internal_account,external_account):
		self.id = id
		self.account_no = account_no
		self.customer_name = customer_name

		self.mobile = mobile
		self.email = email 
		self.code = code
		self.api_token = api_token
		self.api_key = api_key
		self.created_at = created_at
		self.sms_verify_status = sms_verify_status
		self.email_verify_status = email_verify_status
		self.status = status
		self.statement_path = statement_path
		self.branch_code = branch_code
		self.internal_account = internal_account
		self.external_account = external_account
		
		#self.user_otp = user_otp
		#self.created_at = created_at

	def __repr__(self):
		return f"<Item {self.email}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "account_no": self.account_no,
				 "mobile": self.mobile,
				 "email": self.email,      
				 "code":self.code,
				 "api_token":self.api_token,
				 "api_key":self.api_key,
				 "created_at":self.created_at,
				 "sms_verify_status" : self.sms_verify_status,
				 "email_verify_status":self.email_verify_status,
				 "status" : self.status,
				 "statement_path" : self.statement_path,
				 "branch_code" : self.branch_code,
				 "internal_account" : self.internal_account,
				 "external_account" : self.external_account
				}



class TININFO(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "tin_info"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)
	#id = db.Column(db.Integer, primary_key=True)
	account_no = db.Column("account_no",db.String(15), nullable=False)
	tin_no = db.Column("tin_no",db.String(20), nullable=False)
	mobile = db.Column(db.String(13), nullable=False)
	email = db.Column(db.String(155), nullable=False)
	token = db.Column("token",db.Text , nullable=False)
	api_token = db.Column("api_token",db.String(15) , nullable=False)
	financial_year = db.Column("financial_year",db.String(15) , nullable=False)
	otp_status = db.Column("otp_status", db.Integer,nullable=False)
	status = db.Column("status", db.Integer,nullable=False)
	tin_return_file = db.Column("tin_return_file",db.String(200) , nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	branch_code = db.Column("branch_code",db.String(4) , nullable=False)
	card_no = db.Column("card_no",db.String(20) , nullable=True)
	maker_by = db.Column("maker_by",db.String(220) , nullable=True)
	approve_by = db.Column("approve_by",db.String(20) , nullable=True)
	customer_basic = db.Column("customer_basic",db.String(15) , nullable=True)
	updated_at = db.Column("updated_at",db.DATETIME , nullable=False)

	#otp_tries = db.Column("otp_tries", db.Integer)
	#user_otp = db.Column("user_otp",db.String(120) , nullable=False)
	
	#sms_verify_status = db.Column("sms_verify_status", db.Integer,nullable=False)
	#email_verify_status = db.Column("email_verify_status", db.Integer,nullable=False)
	
	#statement_path = db.Column("statement_path",db.String(500) , nullable=False)
	#api_key = db.Column("api_key",db.Text , nullable=False)
	#code = db.Column("code",db.String(120) , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#status = db.Column("status", db.Integer,nullable=False)
	

	def __init__(self,id,account_no,tin_no,mobile,email,token,api_token,financial_year,otp_status,status,tin_return_file,created_at,branch_code,card_no,maker_by,approve_by,customer_basic,updated_at):
		self.id = id
		self.account_no = account_no
		self.tin_no = tin_no
		self.mobile = mobile
		self.email = email 
		self.token = token
		self.api_token = api_token
		self.financial_year = financial_year
		self.otp_status = otp_status
		self.status = status
		self.tin_return_file = tin_return_file
		self.created_at = created_at
		self.branch_code = branch_code
		self.card_no = card_no
		self.maker_by = maker_by
		self.approve_by = approve_by
		self.customer_basic = customer_basic
		self.updated_at = updated_at
		
		#self.statement_path = statement_path
		
		#self.user_otp = user_otp
		#self.created_at = created_at

	def __repr__(self):
		return f"<Item {self.email}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "account_no": self.account_no,
				 "tin_no": self.tin_no,
				 "mobile": self.mobile,
				 "email": self.email,      
				 "token":self.token,
				 "api_token":self.api_token,
				 "financial_year":self.financial_year,
				 "status" : self.status,
				 "otp_status" : self.status,
				 "created_at":self.created_at,
				 "tin_return_file" : self.tin_return_file,
				 "branch_code" : self.branch_code,
				 "card_no" : self.card_no,
				 "maker_by":self.maker_by,
				 "approve_by" : self.approve_by,
				 "customer_basic" : self.customer_basic,
				 "updated_at" : self.updated_at



				}


class Branches(db.Model):

	"""
	Defines the items model
	"""

	__tablename__ = "branches"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	#BranchName,Mnemonic,Code,SubBranch

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)

	BranchName = db.Column("BranchName",db.String(225), nullable=False)
	Mnemonic = db.Column("Mnemonic",db.String(6), nullable=False)
	Code = db.Column("Code",db.String(6), nullable=False)
	SubBranch = db.Column("SubBranch",db.String(10), nullable=False)

	def __init__(self,id,BranchName,Mnemonic,Code,SubBranch):

		self.id = id
		self.BranchName = BranchName
		self.Mnemonic = Mnemonic
		self.Code      = Code
		self.SubBranch = SubBranch

	def __repr__(self):
		return f"<Item {self.Mnemonic}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "BranchName" : self.BranchName,
				 "Mnemonic" : self.Mnemonic,
				 "Code" : self.Code,
				 "SubBranch" : self.SubBranch
				}


	
class REMITCUSTINFO(db.Model):
	"""
	Defines the items model
	"""

	__tablename__ = "remitcustinfo"
	__table_args__ = {"schema":"abbl"}
	#__bind_key__ = 'otp_db_bind'
	__bind_key__ = 'otp_db_bind'

	id = db.Column("id", db.BIGINT, autoincrement=True,primary_key=True)
	#id = db.Column(db.Integer, primary_key=True)
	account_no = db.Column("account_no",db.String(15), nullable=False)
	customer_name = db.Column("customer_name",db.String(255), nullable=False)
	mobile = db.Column(db.String(13), nullable=False)
	email = db.Column(db.String(155), nullable=False)
	code = db.Column("code",db.String(120) , nullable=False)
	api_token = db.Column("api_token",db.String(6) , nullable=False)
	api_key = db.Column("api_key",db.Text , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#user_otp = db.Column("user_otp",db.String(120) , nullable=False)
	created_at = db.Column("created_at",db.DATETIME , nullable=False)
	sms_verify_status = db.Column("sms_verify_status", db.Integer,nullable=False)
	email_verify_status = db.Column("email_verify_status", db.Integer,nullable=False)
	status = db.Column("status", db.Integer,nullable=False)
	statement_path = db.Column("statement_path",db.String(500) , nullable=False)
	branch_code = db.Column("branch_code",db.String(6) , nullable=False)
	internal_account = db.Column("internal_account",db.String(20) , nullable=False)
	external_account = db.Column("external_account",db.String(20) , nullable=False)
	address = db.Column("address",db.Text , nullable=False)
	#api_key = db.Column("api_key",db.Text , nullable=False)
	#code = db.Column("code",db.String(120) , nullable=False)
	#otp_tries = db.Column("otp_tries", db.Integer)
	#status = db.Column("status", db.Integer,nullable=False)
	

	def __init__(self,id,account_no,customer_name,mobile,email,code,api_token,api_key,created_at,sms_verify_status,email_verify_status,status,statement_path,branch_code,internal_account,external_account,address):
		self.id = id
		self.account_no = account_no
		self.customer_name = customer_name

		self.mobile = mobile
		self.email = email 
		self.code = code
		self.api_token = api_token
		self.api_key = api_key
		self.created_at = created_at
		self.sms_verify_status = sms_verify_status
		self.email_verify_status = email_verify_status
		self.status = status
		self.statement_path = statement_path
		self.branch_code = branch_code
		self.internal_account = internal_account
		self.external_account = external_account
		self.address = address
		
		#self.user_otp = user_otp
		#self.created_at = created_at

	def __repr__(self):
		return f"<Item {self.email}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""
		return { 
				 "id" : self.id,
				 "account_no": self.account_no,
				 "mobile": self.mobile,
				 "email": self.email,      
				 "code":self.code,
				 "api_token":self.api_token,
				 "api_key":self.api_key,
				 "created_at":self.created_at,
				 "sms_verify_status" : self.sms_verify_status,
				 "email_verify_status":self.email_verify_status,
				 "status" : self.status,
				 "statement_path" : self.statement_path,
				 "branch_code" : self.branch_code,
				 "internal_account" : self.internal_account,
				 "external_account" : self.external_account,
				"address" : self.address
				}

