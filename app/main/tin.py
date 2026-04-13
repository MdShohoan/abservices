import os
import re
import datetime
import requests
import random
from sqlalchemy.orm.session import Session
import xmltodict
import json
import csv
import math
import logging
import logging.config
from zeep import Client
from zeep.transports import Transport
import pyodbc
#import pymssql

from logging.handlers import TimedRotatingFileHandler
import xlsxwriter
import json
import random
import xmltodict
import smtplib


#import requests
#import datetime
#import json

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from smtplib import SMTPException

import uuid
from flask import render_template, send_file
from flask import Blueprint,Markup, current_app,render_template, url_for, request,session, redirect,jsonify,redirect,flash,abort
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_wtf.csrf import CSRFError
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO
from werkzeug.utils import secure_filename

# import the main blue print instance
#from app.main.profile import profile
from app.main import tin
import app.utils
from app import db 
from app import LOG
tin = Blueprint('tin', __name__, url_prefix='/tin')



logging.getLogger("requests").setLevel (logging.WARNING)
logging.getLogger("zeep").setLevel (logging.WARNING)
logging.getLogger("urllib3").setLevel (logging.WARNING)
logging.getLogger("werkzeug").setLevel (logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel (logging.ERROR)
logging.getLogger("sqlalchemy.engine.Engine").setLevel (logging.ERROR)

eqConnectwsdl = current_app.config['EQCONNECTWSDL']
eqEnqurywsdl = current_app.config['EQENQUIRYWSDL']
eqTransactionwsdl = current_app.config['EQTRANSACTIONWSDL']

CBS_SYSTEM      = current_app.config['CBS_SYSTEM']
CBS_UNIT        = current_app.config['CBS_UNIT']
CBS_USERNAME    = current_app.config['CBS_USERNAME']
CBS_PASSWORD    = current_app.config['CBS_PASSWORD']

#ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif','pdf'])
ALLOWED_EXTENSIONS = current_app.config['ALLOWED_EXTENSIONS']

MAX_CONTENT_LENGTH = current_app.config['MAX_CONTENT_LENGTH']

UPLOAD_FOLDER = '../static/uploads/'
DB_UPLOAD_FOLDER = '/static/uploads/'

MAX_CONTENT_LENGTH = 16 * 1024 * 1024

request_cbs_login_data = {
	'clientAppId':'abpythonapps',
	'system' :CBS_SYSTEM,
	'unit'	: CBS_UNIT,
	'user' :  CBS_USERNAME,
	'pass' : CBS_PASSWORD
}

dt = datetime.datetime.now()

def convert_size(size_bytes):
   if size_bytes == 0:
	   return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@tin.route('/', methods=['GET', 'POST'])
def index():
	#print ('Hello World !!!')
	error = None
	customer_found = False
	request_type = 'tin'
	if request.method == 'POST':
		otp_result          = False
		ssl_otp_response    = {}
		accnt_no            = request.form.get('accnt_no')
		frm_csrf_token =  request.form.get('csrf_token') 
		LOG.debug('Verify account no %s',accnt_no )
		csrf =   generate_csrf()
		dt = datetime.datetime.now()
		requestid = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
		customer_found,customer_data = app.utils.do_account_verifiy(requestid,accnt_no,csrf)
		print (customer_data)

		if customer_found : 
			
			'''if customer_data['email1']:
				flash ('You already have an Email. To update email , please contact with Branch. ')
				return render_template('abemail.html')
			'''
			#print ("Result Found")
			#print ("Account Summaries : " + result['customerName'])
			#return render_template('otp.html')
			LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
			otp_result,ssl_otp_response = app.utils.send_otp (accnt_no,customer_data,request_type)
			print (otp_result)
			#LOG.debug('Verify account no %s : SSL response data : ',accnt_no,ssl_otp_response )
			if otp_result:
				LOG.debug('Verify account no %s : SSL response data :%s ',accnt_no,ssl_otp_response )
				view_otp_send_date = ssl_otp_response['view_otp_send_date']
				masked_mobile = ssl_otp_response['customer_mask_mobile']
				masked_account_number = ssl_otp_response['customer_account_number']
				msg             = "An OTP has been send to your Mobile. Please verify. "
				customer_name   =  customer_data.get('customerName')
				requestid       = customer_data.get('requestid')
				mobile          =  customer_data.get('mobile')
				branch_code     =  customer_data.get('branch_code')
				internal_account = customer_data.get('internal_account')
				external_account = customer_data.get('external_account')
				if not mobile :
					mobile = '01673615816'
				basicNumber     = customer_data.get('basicNumber')
				request_type    = 'tin'
				jsdata          = {'baseurl': current_app.config["BASE_URL"] }
				LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
				jsdata = {'baseurl': current_app.config["BASE_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid}
				
				id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
				
				try:
					new_request = CUSTINFO(id=id,account_no=basicNumber,customer_name = customer_name,mobile=mobile,email= '',code='',api_token=requestid,api_key=csrf,created_at=dt,sms_verify_status=0,email_verify_status=0,status=0,statement_path='',branch_code=branch_code,internal_account=internal_account,external_account=external_account)
					db.session.add(new_request)
					db.session.commit()
					flash (msg)
				except:
					db.session.rollback()
					raise

				finally:
					db.session.close()  # optional, depends on use case
				
				return render_template('otp.html', otp_send_date = view_otp_send_date,
										customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=msg,trackingcode=requestid,type=request_type,jsdata=jsdata)


		return render_template('tin/index.html')
	
	else:
		return render_template('tin/index.html')

@tin.route('/home/<requestid>/', methods=['GET', 'POST'])
def home(requestid):
	error = None
	customer = CUSTINFO.query.filter_by(api_token=requestid).first()
	return render_template('tin/index.html')

@tin.route('/success', methods=['GET', 'POST'])
def success():
	return render_template('tin/success.html')

@tin.route('/uploader/<requestid>', methods = ['GET', 'POST'])
def upload_file(requestid):
	error = None
	dt = datetime.datetime.now()
	customer = CUSTINFO.query.filter_by(api_token=requestid).first()
	if customer:
		email       = customer.email
		mobile 		= customer.mobile
		cbs_basic   = customer.account_no
		branch_code = customer.branch_code
		basic_number = customer.account_no
		external_account = customer.external_account
		customer_name = customer.customer_name
		masked_account_number    = external_account[0:3]+len(external_account[:-8])*"*"+external_account[-4:]

	print (customer)
	print ('file upload')
	if request.method == 'POST':
		

		if 'tinfile' not in request.files:
			flash('No file part')
			return redirect(request.url)

		

		
		filename = ''
		#account_no = request.files['account_no']
		file = request.files['tinfile']
		#filesize = os.stat(file).st_size
		filesize = file.seek(0,os.SEEK_END)
		csize = convert_size(filesize)
		file.seek(0, os.SEEK_SET)
		print ('file size ..')
		print (filesize)
		print (csize)
		
		if 'KB' in  csize :
			is_max_limit = 1 
		else: 
			is_max_limit = 0
			flash('Your uploaded file exceeded maximum length.')
			return redirect(request.url)


		if file.filename == '':
			flash('No image selected for uploading')
			return redirect(request.url)
	
		if file and allowed_file(file.filename):
			now = datetime.datetime.now()
			created_at=  now.strftime("%Y-%m-%d %H:%M:%S")
			file_dt=  now.strftime("%Y_%m_%d_%H_%M_%S")
			
			account_no = cbs_basic
			tin_no = request.form['tin_no']
			token= request.form['csrf_token']
			api_token = request.form['csrf_token']
			
			#filename =  basic_number+"_"+tin_no+secure_filename(file.filename)
			filename =  basic_number+"_"+tin_no+file_dt+secure_filename(file.filename)
			basedir = os.path.abspath(os.path.dirname(__file__))
			full_file_name = DB_UPLOAD_FOLDER+""+filename
			print (full_file_name)
			#file_stats = os.stat()

			file.save(os.path.join(os.path.join(basedir,UPLOAD_FOLDER, filename)))
			id 	= int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
			#account_no =request.form['account_no']
			
			email =email
			mobile =mobile
			financial_year = request.form['finyear']
			otp_status  = 1
			status = 0 # maker end
			
			
			tin_return_file = full_file_name
			tin_no =  request.form['tin_no']
			#external_account =  request.form['external_account']
			#card_no =  request.form['card_no']
			card_no = ''
			maker_by = customer_name
			approve_by = ''
			customer_basic = basic_number
			updated_at = ''
			
			try:
			
				new_request = TININFO(id=id,account_no=external_account,tin_no=tin_no,token=token,api_token=api_token,email= email,mobile=mobile,financial_year=financial_year,otp_status=otp_status,status=status,created_at=dt,tin_return_file=tin_return_file,branch_code=branch_code,card_no=card_no,maker_by=maker_by,approve_by=approve_by,customer_basic=customer_basic,updated_at=dt)
				#print( new_request)
				db.session.add(new_request)
				db.session.commit()
				#print ('db addedd')
				#flash('TAX Return file successfully uploaded ')
			except:
				db.session.rollback()
				raise
			finally:
				db.session.close()  # optional, depends on use case
			
			return render_template('tin/success.html', filename=filename)
		
		
		else: 
			flash('Allowed image types are -> png, jpg, jpeg, gif,pdf')
			return redirect(request.url)
	else:
		#print ('Hello World !!!')
		
		return render_template('tin/tin_new.html',requestid=requestid,customer_name = customer_name,masked_account_number=masked_account_number)



def update_tin_cbs(requestid,tin_data,custMnem,taxCountryCode='BD'):
	
	api_response = False
		
	try:
	   
		LOG.info("******* Api call api ,  : %s Requestid  :%s*******",requestid,email)
		client =Client(wsdl = eqConnectwsdl)
		LOG.info("******* Account :%s*****customer : %s**",requestid,email)
		sessiontoken =  client.service.login(**request_cbs_login_data)
		if sessiontoken :     
			LOG.info('Account: %s: , session token : %s  ', requestid, sessiontoken)
			transactionClient = Client(eqTransactionwsdl)
			request_data = { 
				'sessionToken' : sessiontoken,
				'custMnem' : custMnem,
				'custLoc' : "",
				'email1' : email,
				'taxId':tin_data,
				'taxCountryCode':taxCountryCode
				

			}
			cusresult = transactionClient.service.addCustomerDetails(**request_data)
			LOG.info('Account: %s: , Cust details Result Data : : %s  ',requestid, cusresult)
			#LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
			#cusresult = transactionClient.service.customerDetails(**request_data)
			#LOG.info('Account: %s: , Cust details Result Data : : %s  ', custno, cusresult)
			print (cusresult)
			print ('Email Update ok')
			result = client.service.logout (sessiontoken)
			LOG.debug('Account: %s: , Logout Result Data : : %s  ', requestid, result)
			return  cusresult['success']
			
			'''if cusresult['success'] == 'true' :
				print ('ok')
			else:
				print ('failed')'''
	except Exception as e:
		print (e)
		LOG.error("Account: %s: Error  %s",requestid, email) 
		return api_response