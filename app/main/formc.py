import os
import re
import datetime
import requests
import random
import uuid
from flask import render_template, send_file
from flask import Blueprint,Markup, current_app,render_template, url_for, request,session, redirect,jsonify,redirect,flash,abort
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_wtf.csrf import CSRFError
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO,REMITCUSTINFO
from werkzeug.utils import secure_filename
import logging
import logging.config
from sqlalchemy.orm.session import Session
#from logging.handlers import TimedRotatingFileHandler
from app.main import formc
import app.utils
from app import db 
from app import LOG
from app.dbmodels.formc import Remittance,Remittance_Purpose
formc = Blueprint('formc', __name__, url_prefix='/formc')


@formc.route('/', methods=['GET', 'POST'])
def home():
	error = None
	customer_found = False
	request_type = 'formc'
	if request.method == 'POST':
		accnt_no            = request.form.get('accnt_no')
		frm_csrf_token  =  request.form.get('csrf_token') 
		LOG.debug('*******Verify account no for Form-C: %s *****',accnt_no )
		
		csrf =   generate_csrf()
		dt = datetime.datetime.now()
		requestid = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
		customer_found,customer_data = app.utils.do_account_verifiy(requestid,accnt_no,csrf)
		LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
		if customer_found :
			mobile = customer_data.get('mobile')
			otp_result,ssl_otp_response = app.utils.send_otp (accnt_no,customer_data,request_type)
			#LOG.debug('Verify account no %s : SSL response data : ',accnt_no,ssl_otp_response )
			#print (f"otp result : "+otp_result)
			if otp_result:
				#LOG.debug('Verify account no %s : SSL response data :%s ',accnt_no,ssl_otp_response )
				view_otp_send_date = ssl_otp_response['view_otp_send_date']
				masked_mobile = ssl_otp_response['customer_mask_mobile']
				masked_account_number = ssl_otp_response['customer_account_number']
				msg             = "An OTP has been sent to your Mobile.Please verify. "
				customer_name   =  customer_data.get('customerName')
				requestid       = customer_data.get('requestid')
				mobile          =  customer_data.get('mobile')
				branch_code     =  customer_data.get('branch_code')
				internal_account = customer_data.get('internal_account')
				external_account = customer_data.get('external_account')
				basicNumber     = customer_data.get('basicNumber')
				address     = customer_data.get('address')
				#request_type    = 'sms'
				jsdata          = {'baseurl': current_app.config["BASE_URL"] }
				LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
				jsdata = {'baseurl': current_app.config["BASE_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid}
				id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
				new_request = REMITCUSTINFO(id=id,account_no=basicNumber,customer_name = customer_name,mobile=mobile,email= '',code='',api_token=requestid,api_key=csrf,created_at=dt,sms_verify_status=0,email_verify_status=0,status=0,statement_path='',branch_code=branch_code,internal_account=internal_account,external_account=external_account,address=address)
				db.session.add(new_request)
				db.session.commit()
				flash (msg)
				return render_template('otp.html', otp_send_date = view_otp_send_date,
										customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=msg,trackingcode=requestid,type=request_type,jsdata=jsdata)


	return render_template('formc/home.html')


@formc.route("/verify/<code>/<type>/",methods = ['GET', 'POST'])
def otp_verify(code,type):
	
	#if not session['session_csrf']:
		#print ('session expired')
		#return jsonify({"error": f"Item {code} not found"})
	
	LOG.debug("***********************%s: *****verify  OTP start  ***********",code)
	print (type)
	print (request.method)
	if request.method == "POST":
		try:
			#item = OTPModel.query.filter_by(code=code).first_or_404()
			code = request.form['otp']
			csrf = request.form['csrf_token']
			
			trackingcode = request.form['trackingcode']
			
			session['trackingcode'] = trackingcode
			session['session_csrf'] = csrf
			
			request_type = request.form['request_type']
			url = current_app.config["BASE_URL"]
			LOG.debug("***********************%s: ***** User Input OTP ****:%s*******",trackingcode,code)
			LOG.debug("** Tracking COde  :%s,*OTP:%s,* CSRF****:%s*******",trackingcode,code,csrf)
			db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first()
			LOG.debug("** otpinfo :%s",db_result_item)
			LOG.debug("** db result :%s",db_result_item)
			LOG.debug("** db result api key :%s",db_result_item.api_key)
			
			
			
			
			now  = datetime.datetime.now()
			otp_send_date  = now.strftime("%Y-%m-%d %H:%M:%S")
			dt =  datetime.datetime.now()
			id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
			new_otp_history = OTP_HISTORY(id=id,mobile=db_result_item.mobile,code= db_result_item.code,user_otp=code,api_token=trackingcode,created_at=otp_send_date)
			db.session.add(new_otp_history)
			db.session.commit()
			
			
			#print (db_result_item)
			#print ("OTP Tries :")
			#print (db_result_item.otp_tries)            
			LOG.debug("***********************Check OTP Expired result*********:%s*******",trackingcode)
			otp_expired_status,url = app.utils.checkOTPExpired(trackingcode,db_result_item.created_at,current_app.config['OTP_EXPIRE_TIME'])
			
			url = url + 'formc/home/'+trackingcode+'/'+request_type
			#print ('*************url:********** ')
			#print (url)
			if otp_expired_status:
				
				LOG.debug("***********************Get OTP Error**:%s**,redirect url:***%s**",trackingcode,url)
				session.pop('trackingcode', None)
				session.pop('session_csrf', None)
				return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"OTP Session Time Expired . "})
			
			LOG.debug("*****Check OTP Limit:***trackingcode:******:%s OTP TRIES:*****%s*",trackingcode,db_result_item.otp_tries)
			
			otp_limit_status,url = app.utils.checkOTPLimitExceed(trackingcode,current_app.config['MAX_OTP_LIMIT'],db_result_item.otp_tries)
			
			if otp_limit_status: 
				#opt_limit_url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
				LOG.debug("***********************OTP Limit Error**:%s**,redirect url:***%s**",trackingcode,url)
				opt_limit_url = url
				session.pop('trackingcode', None)
				session.pop('session_csrf', None) 
				return jsonify({"status":"fail"},{"redirectUrl":opt_limit_url},{"message": f"Maximum 3 times you can try . "})
			
			LOG.debug("**Query to Match with DB : tracking code:***%s***********OTP:*******%s: *****  * CSRF:***:%s*******",trackingcode,code,csrf)
			
			item = OTPModel.query.filter(OTPModel.code == code,OTPModel.api_token == csrf,OTPModel.api_key == trackingcode).first()
			#print (jsonify(item.serialize))
			if item:
				LOG.debug("**Updateh DB Status ***********")
				item.otp_tries = item.otp_tries + 1
				item.status = 1
				db.session.commit()

				url = current_app.config["BASE_URL"]
				#url = url + 'email/' + trackingcode
				#print ("initial return url : " + url)
				#CUSTINFO.query.filter()
				replyItem = SMSINFO.query.filter(SMSINFO.trackingcode == trackingcode).first()
				
				if replyItem.message == "Verify":
					#url = replyItem.callback_url
					#url  = url
					url = url + 'formc/home/' + trackingcode+'/'+request_type


					return jsonify({"status":"success"},{"redirectUrl":url},item.serialize )
					#return jsonify({"status":"warning"},{"resultCode":"abcustom"},{"message": f"OTP  {code} does not match. please try again."})        

				else:         
					
					
					if (request_type == 'formc'):
						url = url + 'formc/home/' + trackingcode+'/'+request_type
					
					
					response = {
						'status': 'success',
						'result': 'sms sent',
						'code' : code,
						'phone': item.mobile,
						'message': 'Verify',
						'reference_no': 'None',
						'ssl_reference_no': 'None',
						'sms_send_time' :datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p'),
						'ssl_reply_message' : 'Verify',
						'trackingcode' : trackingcode,
						'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p'),
						'callback_url' :url
						}
					
					#print ("ssl insert ")
					#print (response['status'])
					app.utils.add_ssl_otp(response,trackingcode)
					#print ("Success return url : " + url)
					LOG.debug("***********************%s: ***Succuess Redirect URL****:%s*******",trackingcode,url)
					item = REMITCUSTINFO.query.filter(REMITCUSTINFO.api_token == trackingcode).first()                    
					if item:
						LOG.debug("**Update DB Status ***********")
						#item.otp_tries = item.otp_tries + 1
						item.sms_verify_status = 1
						db.session.commit()
					
					
					#session.pop('trackingcode', None)
					#session.pop('session_csrf', None)
				   
					return jsonify({"status":"success"},{"redirectUrl":url},item.serialize )
			else:

				#print ('increase tries')
				LOG.debug("*******Error : ****************%s: ***** OTP: ****:%s*** does not match.****",trackingcode,code)
				#db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first_or_404()
				db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first_or_404()
				#print ("OTP Tries in error :")
				#print (db_result_item.otp_tries)
				db_result_item.otp_tries       = db_result_item.otp_tries + 1
				LOG.debug("***********************%s: ***** OTP TRies : ****:%s*******",trackingcode,db_result_item.otp_tries)
				db_result_item.status = 0
				db.session.commit()
				
				#print ('check ')
				#print ('db result....')
				#print (db_result_item.otp_tries)

				if (db_result_item.otp_tries >=current_app.config['MAX_OTP_LIMIT']):
					#otp_limit_status,url = app.utils.checkOTPLimitExceed(trackingcode,current_app.config['MAX_OTP_LIMIT'],db_result_item.otp_tries,current_app.config['BKASH_API_URL'],request_type)
					#print (otp_limit_status)
					#print (url)
					LOG.debug("***********************%s: ***** OTP TRies : ****:%s*******",trackingcode,db_result_item.otp_tries)
					session.pop('trackingcode', None)
					session.pop('session_csrf', None)
					
					
					return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"Maximum 3 times you can try . "})
				
				#print ('status : warning')
				return jsonify({"status":"warning"},{"resultCode":"abcustom"},{"message": f"OTP  {code} does not match. please try again."})
				#print (item)
		except Exception as error:
			#print (error)
			session.pop('trackingcode', None)
			session.pop('session_csrf', None)
			return jsonify({"status":"error"},{"message": f"Tracking code  not found"},{"status":" fail"})
	else:
		# only for test purpose
		items = OTPModel.query.filter((OTPModel.code == code)).first_or_404()
		#print ("get ...")
		#print (items)
		#print (jsonify([item.serialize for item in items]))
		#return jsonify([item.serialize for item in items])
		
		'''item.append({
				"Name": "Person_3",
				"Age": 33,
				"Email": "33@gmail.com"
		})'''
		#print (jsonify(item.serialize))
		#result = jsonify(item.serialize)
		'''result.append({
				"Name": "Person_3",
				"Age": 33,
				"Email": "33@gmail.com"
		})'''

		#return items
		return {"message": "success"}

@formc.route('/home/<trackingcode>/<request_type>', methods=['GET', 'POST'])
def index(trackingcode,request_type):
	
	
	
	#session.pop('trackingcode', None)
	#session.pop('session_csrf', None)
	

	
	applicant_address =''
	purposes = Remittance_Purpose.query.all()
	LOG.debug("***********************%s: ***Succuess*******",trackingcode)
	custinfo = REMITCUSTINFO.query.filter(REMITCUSTINFO.api_token == trackingcode).first()
	
	
	
	#print ('Customer Info : ')
	#print (custinfo)                 
	if custinfo:
		LOG.debug("**Update DB Status ***********")
		#item.otp_tries = item.otp_tries + 1
		#item.sms_verify_status = 1
		applicant_name = custinfo.customer_name
		applicant_mobile = custinfo.mobile
		applicant_address = custinfo.address
		#print ('Address')
		#print (applicant_address)

		
	#print (purposes)
	if request.method == 'POST':
		#print ('form submitted..')
		ictPurposeSpecify = ''
		remittance_reference = ''

		frm_csrf_token  =  request.form.get('csrf_token') 
		remitter_name   = request.form.get ('remitter_name')
		remitter_address = request.form.get ('remitter_address')
		remittance_amount = request.form.get ('remittance_amount')
		remittance_currency = request.form.get ('remittance_currency')
		remitted_bank_name = request.form.get ('remitted_bank_name')
		remitted_bank_address =  request.form.get ('remitted_bank_address')
		remittance_type =   request.form.get ('remittance_type')
		opt =   request.form.get ('opt')
		#print ('OPT : ')
		#print (opt)
		
		ictPurposeSpecify = request.form.get ('ictPurposeSpecify')
		purposeSpecify = request.form.get ('purposeSpecify')
		#purpose = request.form.get ('purpose')
		applicant_name = request.form.get ('applicant_name')
		applicant_address = request.form.get ('applicant_address')
		application_date = request.form.get ('application_date')
		applicant_nationality = request.form.get ('nationality')
		applicant_mobile = request.form.get ('applicant_mobile')
		remittance_reference = request.form.get ('remittance_reference')
		remittance_amount_words = ''
		
		

		if ( remittance_type =='ICT' ):
			ictPurposeSpecify = ictPurposeSpecify
			purpose_of_remittance_id = int(opt)
		else:
			ictPurposeSpecify = purposeSpecify
			purpose_of_remittance_id = 0
		
		dt = datetime.datetime.now()
		print_status = 0
		printed_by = 0
		#print ('ictPurposeSpecify : ')
		#print (ictPurposeSpecify)
		
		try:
			id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
			#(self,id,remitter_name,remitter_address,remittance_amount,remittance_currency,remitted_bank_name,remitted_bank_address,purpose_of_remittance_id,applicant_name,applicant_nationality,applicant_address,application_date,print_date,print_status,printed_by,remittance_type)
			#id =1 
			new_request = Remittance(id,remitter_name=remitter_name,remitter_address = remitter_address,remittance_amount=remittance_amount,remittance_currency= remittance_currency,remitted_bank_name=remitted_bank_name,remitted_bank_address=remitted_bank_address,purpose_of_remittance_id=purpose_of_remittance_id,applicant_name=applicant_name,applicant_nationality=applicant_nationality,applicant_address=applicant_address,application_date=dt,print_date=dt,print_status=print_status,printed_by=printed_by,remittance_type=remittance_type,ictPurposeSpecify=ictPurposeSpecify,applicant_mobile=applicant_mobile,remittance_amount_words=remittance_amount_words,remittance_reference=remittance_reference)
			db.session.add(new_request)
			db.session.commit()
			#flash (msg)
			msg = 'Congratulations!! your Form-C tracking id is : ' + str(id) + '.Visit your branch by next 7 working days.For any Query call 16207'
			flash ('Congratulations !! You have Successfully Added Form-C Data ,Your tracking id is : ' + str(id)+' .Please visit the Branch within next 7 Working days. Also, a Tracking id has been sent to your phone number.','success')
			ssl_otp_response=app.utils.smsnewapi(applicant_mobile,msg)
		except:
			db.session.rollback()
			raise

		return render_template('formc/home.html',purposes=purposes,applicant_name=applicant_name)


	else:
		
		if ('session_csrf' not in session):
			print ('session expired')
			flash ('Sorry ! You have no access.')
			return redirect('/')
			#return jsonify({"error": f"Item {code} not found"})
	
		if  (session['trackingcode'] != trackingcode):
			flash ('Sorry ! You have no access.')
			return redirect('/')
		
		session.pop('trackingcode', None)
		session.pop('session_csrf', None)
		return render_template('formc/index.html',purposes=purposes,applicant_name=applicant_name,applicant_mobile=applicant_mobile,applicant_address=applicant_address,trackingcode=trackingcode,request_type=request_type)
