import re
from flask import render_template
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

from logging.handlers import TimedRotatingFileHandler
import xlsxwriter
import json
import random
import xmltodict
import smtplib
#import lib

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from smtplib import SMTPException

import uuid
from flask import Blueprint,Markup, current_app,render_template, url_for, request,session, redirect,jsonify,redirect,flash,abort
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_wtf.csrf import CSRFError
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS

# import the main blue print instance
from app.main import main

import app.utils
from app import db 
from app import LOG


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

#is_debug = current_app.config['BASE_URL']

#print (current_app.config['EQCONNECTWSDL'])

request_cbs_login_data = {
	'clientAppId':eqConnectwsdl,
	'system' :CBS_SYSTEM,
	'unit'	: CBS_UNIT,
	'user' :  CBS_USERNAME,
	'pass' : CBS_PASSWORD
}

dt = datetime.datetime.now()

def encode(message):
    #return message.encode('utf-16-be').hex().upper()
    return message.encode('utf-8')

@main.route("/test",methods = ['GET'])
def test():

    try:
        
        dt 						  = datetime.datetime.now()
        dt2= dt.strftime("%Y%m%d%H%M%S%f")
        id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
        
        print ("date.." +dt2 )
        print ("id")
        print (id)
        
        #r = requests.get(url="https://bkashuat.abbl.org:44344/",verify=current_app.config['SSL_CER_FILE'])
        #print (r)
        LOG.debug('string id %s',dt2)
        LOG.debug('string id %s',id)
        LOG.info('So should this')
        LOG.warning('And this, too')
        LOG.error('And non-ASCII stuff, too, like Øresund and Malmö')
        #return render_template('abindex.html', error=id)
        return render_template('abemail.html', error=id)
        #return jsonify({"status":"success"},{"message":"Success"})

        #LOG.debug("******* API CALL TEST*******")
        '''bkash_api_url = current_app.config['BKASH_API_URL']+'/test/encryption'

        headers = {"charset": "utf-8", "Content-Type": "application/json","Username":"bkashabbl","Password":"abbl@123"}

        LOG.debug("******* API call for  :%s** url : *****",bkash_api_url )
        LOG.debug("******* API headers:** paramaeter : **%s***",headers )
        username = current_app.config['BKASH_API_URL']
        password = current_app.config['BKASH_API_PASSWORD']
        req_json_data = {"input": "4005457577300"}
        LOG.debug("******* API json data:** paramaeter : **%s***",req_json_data )
        r = requests.post(url=bkash_api_url,auth=(username,password), json=req_json_data,headers=headers)
        LOG.debug("******* API Response for   :%s** url : **%s***",bkash_api_url,r.status_code )
        print(r.status_code, r.reason, r.text)
        return jsonify({"status":"success"},{"message":r.text})'''

    except Exception as error:

        print (error)
        return jsonify({"status":"fail"},{"message": error})


@main.route('/home/<requestid>/', methods=['GET', 'POST'])
def home(requestid):
    error = None
    '''if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    '''
    customer = CUSTINFO.query.filter_by(api_token=requestid).first()

    #customer = OTPModel.query.filter_by(api_key=requestid).first()
    if customer:
        email       = customer.email
        cbs_basic   = customer.account_no
    
    print (cbs_basic)
    print ('email')
    print (email)
    #custinfo = CUSTINFO.query.filter_by(api_token=requestid).first()

    response = update_email_cbs(requestid,email,cbs_basic)
    
    print (response)
    #flash ('Thank You have successfully updated your email address.  ')
    flash(Markup('Thank You have successfully updated your email address, <br> please click <a href="https://abdirect.abbl.com/signup#!"  class="alert-link">here for internet banking</a>'))
    return redirect('/')
    
    #return render_template('login.html', error=error)



def send_otp (account_no,customer_data = {} ) :
    #otp_code = app.utils.otpgen()
    ssl_otp_response ={}
    otp_request_count = 1
    otp_tries = 0
    verify_status = 0
    dt = datetime.datetime.now()
    now                      = datetime.datetime.now()
    otp_send_date            = now.strftime("%Y-%m-%d %H:%M:%S")
    #id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
    requestid                = customer_data.get('requestid')
    customer_name            = customer_data.get('customerName')
    mobile                   = customer_data.get('mobile')
    if not mobile:
        mobile = '01673615816'
    csrf                     = customer_data.get('csrf')
    email                    = customer_data.get('email')
    if  email is None :
        email = 'no-reply@abbl.com' 

    
    
    unmasked                 = str(account_no)
    masked_account_number    = unmasked[0:3]+len(unmasked[:-8])*"*"+unmasked[-4:]
    masked_mobile            = mobile[-3:].rjust(len(mobile), "*")
    csmsid                   = random.randint(1, 99999999)
    
    otp_code                 = app.utils.otpgen()
    otp_msg                  = 'Dear Customer, Your One-Time Password is '+otp_code+ '.Please use this OTP to complete the Email Update.For any Query, call: 16207'
    id= requestid 
    #sms_send (phone,message,id)
    try:
        new_otp = OTPModel(id=id,mobile=mobile,email=email,code= otp_code,api_token=csrf,api_key=requestid,otp_tries=otp_tries,status=verify_status,created_at=otp_send_date,otp_request_count=otp_request_count)
        db.session.add(new_otp)
        db.session.commit()
		#send otp
        LOG.debug("****%s:**** OTP is :%s******",requestid,otp_code) 
        
        ssl_otp_response=app.utils.send_sms_by_ssl(mobile,otp_msg)
        
        
        if ssl_otp_response.get('status') == 'success':
            add_ssl_otp(ssl_otp_response,requestid)
            view_otp_send_date            = now.strftime("%d-%m-%Y %H:%M:%S")
            #print (view_otp_send_date)
            #return render_template('otp.html', otp_send_date = view_otp_send_date,customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=otp_msg,trackingcode=requestid)
            ssl_otp_response.update({'view_otp_send_date': view_otp_send_date,
                                     'customer_mask_mobile':masked_mobile,
                                     'mobile' : mobile, 
                                     'customer_account_number' :masked_account_number,
                                     'customer_name' : customer_name})
                              
            
            return True,ssl_otp_response
        else : 
            return False,ssl_otp_response    
		#lib.send_sms_by_ssl(mobile,'hello world')
        #print ("CSRF3 ")
		#print (csrf)
        #ssl_otp_response['trackingcode'] = requestid
        #print ("ssl insert ")
        #print (ssl_otp_response['status'])
        #print(ssl_otp_response)
        #add_ssl_otp(ssl_otp_response,requestid)

        #jsdata = {'baseurl': current_app.config["BASE_URL"], 'bkash_api_url':  current_app.config["BKASH_API_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid,'bkash_api_username':username,'bkash_api_password':password}
        #print (jsdata)
    except Exception as e:
        return False,ssl_otp_response
        print (e) 

def update_email_cbs(requestid,email,custMnem):
    
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
                'email2' :"",
                'mobilePhone':"",
                'homePhone' : "",
                'businessPhone':"",
                'dateOfBirth':"",
                'taxId':"",
                'taxCountryCode':"",
                'placeOfBirth':"",
                'countryOfBirthCode':"",
                'dependents':"",
                'salary':"",
                'salaryCcy':"",
                'rentMortgage':"",
                'rentMortgageCcy':"",
                'otherExpenses':'',
                'otherExpensesCcy':'',
                'idDocType':'',
                'idDocNumber':'',
                'idDocIssuer':'',
                'idDocIssueDt':'',
                'idDocExpiryDt':'',
                'idDocIssueCountryCode':''

            }
            cusresult = transactionClient.service.addCustomerDetails(**request_data)
            LOG.info('Account: %s: , Cust details Result Data : : %s  ',requestid, cusresult)
            #LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
            #cusresult = transactionClient.service.customerDetails(**request_data)
            #LOG.info('Account: %s: , Cust details Result Data : : %s  ', custno, cusresult)
            print ('ok')
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


def  do_account_verifiy (requestid, account_no,csrf='') :

    try:
        customer_found = False
        session = Session ()
        session.verify = False 
        
        ssl_otp_response = {}
        customer_data = {}
        LOG.info("******* Api call api ,  : %s Requestid  :%s*******",account_no,requestid)
        client =Client(wsdl = eqConnectwsdl)
        #print (client)
     
        if account_no: 
            
            LOG.info("******* Api call for account 2 :%s*******",account_no)
            custno = account_no[4:-3]
            print ('customer')
            print (custno)
            LOG.info("******* Account :%s*****customer : %s**",account_no,custno)
            sessiontoken =  client.service.login(**request_cbs_login_data)
            print (sessiontoken)
            if sessiontoken :     
                    LOG.info('Account: %s: , session token : %s  ', custno, sessiontoken)
                    transactionClient = Client(eqEnqurywsdl)
                    
                    
                    request_data = { 
                        'sessionToken' : sessiontoken,
                        'custno' : custno
                    }
                    
                    LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
                    cusresult = transactionClient.service.customerDetails(**request_data)
                    LOG.info('Account: %s: , Cust details Result Data : : %s  ', custno, cusresult)
                    
                    if cusresult['success'] == True : 
                        
                        customer_name = cusresult['customerName']
                        email1 = cusresult['email1']
                        if not cusresult['mobile']:
                            
                            mobile = '01673615816'
                        else:
                            mobile = cusresult['mobile']
                        #print ("customer name  : " + cusresult['customerName'])
                        customer_found = True
                        dt = datetime.datetime.now()
                        id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3]) 
                        
                        if cusresult['basicNumber'] is None :
                            basicNumber = ""
                        else :
                            basicNumber = cusresult['basicNumber'] 

                        
                        if cusresult['businessPhone'] is None :
                           businessPhone = ""
                        else :
                           businessPhone = cusresult['businessPhone']
                        
                        if cusresult['customerName'] is None :
                            customerName = ""
                        else :
                            customerName = cusresult['customerName']

                    

                        if cusresult['customerType'] is None :
                            customerType = ""
                        else :
                            customerType = cusresult['customerType']

                        if cusresult['customerTypeDesc'] is None :
                            customerTypeDesc = "" 
                        else :
                            customerTypeDesc = cusresult['customerTypeDesc']

                        
                        if cusresult['dateOfBirth'] is None :
                            dateOfBirth = ""
                        else :
                            dateOfBirth = cusresult['dateOfBirth']

                        if cusresult['email1'] is None :
                            email1 = ""
                        else :
                            email1 = cusresult['email1']


                        if cusresult['basicNumber'] is None :
                           email2 = ""
                        else :
                            email2 = cusresult['email2']

                        if cusresult['homePhone'] is None :
                            homePhone = ""
                        else :
                            homePhone= cusresult['homePhone']

                        if cusresult['idDocCode'] is None :
                            idDocCode = ""
                        else :
                            idDocCode = cusresult['idDocCode']

                        if cusresult['idDocNo'] is None :
                            idDocNo = ""
                        else :
                            idDocNo = cusresult['idDocNo']

                        if cusresult['idExpiryDate'] is None :
                            idExpiryDate = ""
                        else :
                            idExpiryDate = cusresult['idExpiryDate']

                        if cusresult['idIssueDate'] is None :
                            idIssueDate = ""
                        else :
                            idIssueDate = cusresult['idIssueDate']

                        if cusresult['idIssuer'] is None :
                            idIssuer = ""
                        else :
                            idIssuer = cusresult['idIssuer']

                        if cusresult['mobile'] is None :
                            mobile = "" 
                        else :
                            mobile = cusresult['mobile']

                        if cusresult['residenceCountry'] is None :
                            residenceCountry = ""
                        else :
                            residenceCountry = cusresult['residenceCountry']

                        if cusresult['taxIdNo'] is None :
                            taxid = ""
                        else :
                            taxid = cusresult['taxIdNo']


                        #basicNumber = cusresult['basicNumber']
                        
                        created_at = dt
                        status = 1 
                        requestid = requestid
                        csrf = csrf
                        customer_data =  {
                                    
                                    'retMessage': cusresult['retMessage'],
                                    'id': id, 
                                    'success': cusresult['success'],
                                    'basicNumber': cusresult['basicNumber'],
                                    'businessPhone': cusresult['businessPhone'],
                                    'customerName': cusresult['customerName'],
                                    'customerType':  cusresult['customerType'],
                                    'customerTypeDesc': cusresult['customerTypeDesc'],
                                    'dateOfBirth': cusresult['dateOfBirth'],
                                    'defaultBranch': cusresult['defaultBranch'],
                                    'email1': cusresult['email1'],
                                    'email2': cusresult['email2'],
                                    'homePhone': cusresult['homePhone'],
                                    'idDocCode': cusresult['idDocCode'],
                                    'idDocNo': cusresult['idDocNo'],
                                    'idExpiryDate': cusresult['idExpiryDate'],
                                    'idIssueDate': cusresult['idIssueDate'],
                                    'idIssuer': cusresult['idIssuer'],
                                    'mobile': cusresult['mobile'],
                                    'residenceCountry': cusresult['residenceCountry'],
                                    'taxid': cusresult['taxIdNo'],
                                    'created_at' : dt,
                                    'requestid':requestid,
                                    'csrf' : csrf,
                        }
                        try:
                            #new_customer_request = CBS_CUSTOMERS(id=id,mobile=mobile,email=email,code= otp_code,api_token=csrf,api_key=requestid,otp_tries=otp_tries,status=verify_status,created_at=otp_send_date,otp_request_count=otp_request_count)
                            new_customer_request = CBS_CUSTOMERS(id=id,basicNumber=basicNumber,businessPhone=businessPhone,customerName= customerName,customerType=customerType,customerTypeDesc=customerTypeDesc,dateOfBirth=dateOfBirth,email1=email1,email2=email2,homePhone=homePhone,idDocCode=idDocCode,idExpiryDate=idExpiryDate,mobile=mobile,residenceCountry=residenceCountry,status=status,taxid=taxid,created_at=dt,requestid= requestid,csrf=csrf)
                            db.session.add(new_customer_request)
                            db.session.commit()
		                    #send otp
                            LOG.debug("****%s:**** New custommer request is :%s******",requestid,customer_data) 
                        except Exception as e:
                            print (e)
                            LOG.error("Account: %s: Error  %s",account_no, e) 
                            return customer_found,customer_data
                            

                    else : 
                        LOG.error("Account: %s: API  output  %s",account_no, sessiontoken) 
                        
                    
                    result = client.service.logout (sessiontoken)
                    LOG.debug('Account: %s: , Logout Result Data : : %s  ', custno, result)
                    return customer_found,customer_data


        else:
            LOG.info("******* Account :%s*****Cannot be blank : %s**",account_no)
            return customer_found,customer_data   

    except Exception as e:
        print (e)
        LOG.error("Account: %s: Error  %s",account_no, e) 
        return customer_found,customer_data

 

@main.route('/email/<requestid>/<request_type>', methods=['GET', 'POST'])
#@main.route("/<requestid>/",methods = ['GET'])
def email(requestid,request_type):
    print ("request id : " + requestid)

    if request.method == 'POST':
        print ('OTP send ... ')
        otp_result = False
        ssl_otp_response = {}
        email = request.form.get('email')
        frm_csrf_token =  request.form.get('csrf_token') 
        LOG.debug(' Email   %s',email )
        alert_type = 'email'
        #message = " "
        otp_code                 = app.utils.otpgen()
        message                  = 'Dear Customer, Your One-Time Password is '+otp_code+ '.Please use this OTP to complete the Email Update.For any Query, call: 16207'
        id= requestid
        csrf =   generate_csrf()
        dt = datetime.datetime.now()
        view_otp_send_date =  dt
        customer = CUSTINFO.query.filter_by(api_token=requestid).first()
        
        if email:

            customer.email = email
            db.session.commit()
        
        item = CBS_CUSTOMERS.query.filter_by(requestid=requestid).first()
        
        print ("cbs customer" )
        print (item)
        if item :
            print ('send otp ')
            
            masked_mobile =  item.mobile
            masked_account_number = item.basicNumber
            msg             = "An OTP has been send to your Email. Please verify. "
            accnt_no        = item.basicNumber
            customer_name   =  item.customerName
            #requestid       = customer_data.get('requestid')
            #requestid 		= int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            mobile          =   item.mobile
            basicNumber     = item.basicNumber
            #email           = item.email
            # 
            # 
            dt = datetime.datetime.now()
            id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            #mobile = '01673615834'
            otp_request_count = 1
            otp_tries = 0
			#message = 'test'
            csrf =   generate_csrf()
            print ('csrf.........')
            session['session_csrf']   = csrf
            status = 0
            new_otp = OTPModel(id=id,mobile=mobile,email=email,code= otp_code,api_token=csrf,api_key=requestid,otp_tries=otp_tries,status=status,created_at=dt,otp_request_count=otp_request_count)
            db.session.add(new_otp)
            db.session.commit()
			#send otp
            LOG.debug("****%s:**** OTP is :%s******",requestid,otp_code) 
            #jsdata          = {'baseurl': current_app.config["BASE_URL"] }
            LOG.debug('Verify account no %s : customer data :%s ',accnt_no,item)
            jsdata = {'baseurl': current_app.config["BASE_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid}
            url = current_app.config["BASE_URL"]
            request_type    = 'email'
            response = {
                        'status': 'success',
                        'result': 'sms sent',
                        'code' : otp_code,
                        'phone': item.mobile,
                        'message': 'An otp send to Email',
                        'reference_no': 'None',
                        'ssl_reference_no': 'None',
                        'sms_send_time' :datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p'),
                        'ssl_reply_message' : 'Verify',
                        'trackingcode' : requestid,
                        'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p'),
                        'callback_url' :url
                        }
            print ("ssl insert ")
            print (response['status'])
            add_ssl_otp(response,requestid)
            
            #id= int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            #new_request = CUSTINFO(id=id,account_no=basicNumber,customer_name = customer_name,mobile=mobile,email= '',code='',api_token=requestid,api_key=csrf,created_at=dt,sms_verify_status=0,email_verify_status=0,status=0)
            #db.session.add(new_request)
            #db.session.commit()
            
            
            
            #add_ssl_otp(ssl_otp_response,requestid)
        
        app.utils.send_email_alert (alert_type,email,message,id)
        
        flash ('OTP Has been sent to your email  ')
        return render_template('otp.html', otp_send_date = view_otp_send_date,email=email,
                                        customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=msg,trackingcode=requestid,type=request_type,jsdata=jsdata)
        #frm_url = 
        #return jsonify({"message": f"OTP not generated"},{"status":" success"})

    else:
        request_type    = 'email'
        return render_template('email_entry.html', requestid=requestid,type=request_type)
        #return render_template('email.html', requestid=requestid,type=request_type)




@main.route('/', methods=['GET', 'POST'])
#@main.route("/<requestid>/",methods = ['GET'])
def index():

    error = None
    customer_found = False
    if request.method == 'POST':

        otp_result = False
        ssl_otp_response = {}
        accnt_no = request.form.get('accnt_no')
        frm_csrf_token =  request.form.get('csrf_token') 
        LOG.debug('Verify account no %s',accnt_no )
        
        csrf =   generate_csrf()
        dt = datetime.datetime.now()
        #dt 						  = datetime.datetime.now()
        #dt2= dt.strftime("%Y%m%d%H%M%S%f")
        
        
        requestid = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
        customer_found,customer_data = do_account_verifiy(requestid,accnt_no,csrf)
        LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
        if customer_found : 
            
            '''if customer_data['email1']:
                flash ('You already have an Email. To update email , please contact with Branch. ')
                return render_template('abemail.html')
            '''
            #print ("Result Found")
            #print ("Account Summaries : " + result['customerName'])
            #return render_template('otp.html')
            LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
            otp_result,ssl_otp_response = send_otp (accnt_no,customer_data)
            
            #LOG.debug('Verify account no %s : SSL response data : ',accnt_no,ssl_otp_response )
            if otp_result:
                LOG.debug('Verify account no  2e       %s : SSL response data :%s ',accnt_no,ssl_otp_response )
                view_otp_send_date = ssl_otp_response['view_otp_send_date']
                masked_mobile = ssl_otp_response['customer_mask_mobile']
                masked_account_number = ssl_otp_response['customer_account_number']
                msg             = "An OTP has been send to your Mobile. Please verify. "
                customer_name   =  customer_data.get('customerName')
                requestid       = customer_data.get('requestid')
                mobile          =  customer_data.get('mobile')
                if not mobile :
                    mobile = '01673615816'
                basicNumber     = customer_data.get('basicNumber')
                request_type    = 'sms'
                jsdata          = {'baseurl': current_app.config["BASE_URL"] }
                LOG.debug('Verify account no %s : customer data :%s ',accnt_no,customer_data)
                jsdata = {'baseurl': current_app.config["BASE_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid}
                
                id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
                new_request = CUSTINFO(id=id,account_no=basicNumber,customer_name = customer_name,mobile=mobile,email= '',code='',api_token=requestid,api_key=csrf,created_at=dt,sms_verify_status=0,email_verify_status=0,status=0)
                db.session.add(new_request)
                db.session.commit()
                
                flash (msg)
                
                return render_template('otp.html', otp_send_date = view_otp_send_date,
                                        customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=msg,trackingcode=requestid,type=request_type,jsdata=jsdata)

        return render_template('abemail.html')
        #return render_template('account.html')
    else:
        #flash('Enter Account Number')
        #return render_template('account.html')
        return render_template('abemail.html')
    #if request.method == 'GET':
     

    #print ("Hello World !!!! ")
    #LOG.debug("***********************Start*********:*******")
    #LOG.debug('This message should go to the log file')
    #LOG.info('So should this')
    #LOG.warning('And this, too')
    #LOG.error('And non-ASCII stuff, too, like Øresund and Malmö')
    
    
    #return jsonify({"message": f"OTP not generated"},{"status":" fail"})
    
    '''session.permanent = True
    args = request.args
    LOG.debug("***********************Start*********:%s*******",requestid)
    
    if requestid : 
        try:
            LOG.debug("******* trackingid :%s*******",requestid)
            # test purpose 
           
            #mobile  = "8801791002353"
            #mobile  = "8801711900908"

            #accountNumber = "4005116349300"
            #dataAvailable = True
            #email         = "noreply@abbl.com"
            #customer_name = "Saidur Rahman"
            accountNumber = '' 
            

            #****************************#
            
            #utils.send_sms_by_ssl('8801673615813','hello world')
            #app.logger.info('Processing default request')
            bkash_api_url = current_app.config['BKASH_API_URL']+'/info'
            
            username = current_app.config['BKASH_API_USERNAME']
            password = current_app.config['BKASH_API_PASSWORD']
            
            headers = {"charset": "utf-8", "Content-Type": "application/json","Username":username,"Password":password}
            LOG.debug("******* API call for  :%s** url : *****",bkash_api_url )
            LOG.debug("******* API headers:** paramaeter : **%s***",headers )
            
            request_type= requestid[:2]
            LOG.debug("******* Request Type :%s*******",request_type)
            session['trackingcode']   = requestid 
            #create_row_data = {"requestId":"LN1622139354657"}
            create_row_data = {"requestId":requestid}
            print(create_row_data)
            #print ('test sms')
            LOG.debug("******* API call for  :%s** url : **%s***",requestid,bkash_api_url )
            LOG.debug("******* API call for  :%s** paramaeter : **%s***",requestid,create_row_data )
            #username = current_app.config['BKASH_API_USERNAME']
            #password = current_app.config['BKASH_API_PASSWORD']
            #r = requests.post(url=bkash_api_url,auth=HTTPBasicAuth(username,password), json=create_row_data)
            r = requests.post(url=bkash_api_url,auth=(username,password), json=create_row_data,headers=headers)
            print (requestid)
            LOG.debug("******* API Response for   :%s** url : **%s***",requestid,r.status_code )
            print(r.status_code, r.reason, r.text)
            if r.status_code == 200 :
                records = json.loads(r.text)
                dataAvailable=records["dataAvailable"]
                if dataAvailable:
                    
                    mobile  = records['mobile']
                    if mobile[0:2] != "88":
                        mobile = '88'+mobile


                    print (mobile)
                    accountNumber = records['account']
                    #print (masked_account_number)
                    email                    = 'noreply@abbl.com'
                    #index.logger.info('Info level log')
                    customer_name =records["name"]
                    #customer_name = 'Missing Name'
                else:
                    
                    #utils.
                    otp_expired_status,url = app.utils.otpErroUrl (request_type,bkash_api_url,requestid)
                    LOG.debug("****Error  :%s ********redirect url  :%s******",requestid,url)
                    #r = requests.get(url)
                    #return redirect(url)
                    #return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"Tracking Code Not Found . "})
                    #return jsonify({"message": f"Sorry Account not found"},{"status":" fail"})
            else:
                otp_expired_status,url = app.utils.otpErroUrl (request_type,bkash_api_url,requestid)
                LOG.debug("****Error  :%s ********redirect url  :%s******",requestid,url)
                #r = requests.get(url)
                return redirect(url)

        except Exception as error:  
            #temporaririly added 
            mobile  = "8801673615816"
            #mobile  = "8801791002353"
            #mobile  = "8801711900908"
            accountNumber = "4005116349300"
            dataAvailable = True
            email         = "noreply@abbl.com"
            customer_name = "******"

            
            LOG.debug("****Error  :  %s ********for : %s******",error,requestid)
            #app.logger.info('%s logged in successfully', user.username)
            print (error)
    '''
    '''if len(args) > 1 :
        
            if "name" in args:
                customer_name = args["name"]
    
            if "mobile" in args:
                mobile = args["mobile"]
        
            if "account" in args:
                accountNumber = args["account"]

            if "email" in args: 
                email = args["email"]
    '''
    
    '''if not accountNumber:
        LOG.debug("****Error  :  %s ********for : %s******",requestid)
        #LOG.debug("***********Error : accountNumber :%s** Not Found ***",accountNumber)
        
        return jsonify({"message": f"Sorry Account not found"},{"status":" fail"})   
    
    LOG.debug("****%s**** Mobile:%s******",requestid,mobile)
    LOG.debug("****%s**** Account Number:%s******",requestid,accountNumber)
    LOG.debug("****%s**** Customer Name:%s******",requestid,customer_name)
    LOG.debug("****%s**** Email:%s******",requestid,email)
    
    #print (current_app.config['DEBUG'])
    #print (app.config['DEBUG'])
    #logger.info('Start:')
    #accountNumber = "3456123434561234"
    otp_code                 = app.utils.otpgen()
    now                      = datetime.datetime.now()
    otp_send_date            = now.strftime("%Y-%m-%d %H:%M:%S")
    view_otp_send_date            = now.strftime("%d-%m-%Y %H:%M:%S")
    print (view_otp_send_date)
    
    unmasked                 = str(accountNumber)
    masked_account_number    = unmasked[0:3]+len(unmasked[:-8])*"*"+unmasked[-4:]
    masked_mobile            = mobile[-3:].rjust(len(mobile), "*")
    csmsid                   = random.randint(1, 99999999)
	#print (mobile)
	#id = 1
	#id = uuid.uuid4()
    dt = datetime.datetime.now()
    id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
    #mobile = '01673615834'
    otp_request_count = 1
    otp_tries = 0
    #message = 'test'
    csrf =   generate_csrf()
    print ('csrf.........')
    session['session_csrf']   = csrf
    status = 0
    #sms_send (phone,message,id)
    if request_type =="LN":
        msg = 'By Submitting OTP you are agreeing to link AB Bank Account with bKash Account.'
        otp_msg = 'Dear Customer, Your OTP to link your AB Bank and bKash Account is '+otp_code+ '. For any Query, call: 16207'
    else:
        msg = 'By submitting OTP you are agreeing to Add Money to bKash from AB Bank Account'
        otp_msg = 'Dear Customer, Your OTP to add money to bKash from AB Bank Account is '+otp_code+ '. For any Query, call: 16207'
    try:
        new_otp = OTPModel(id=id,mobile=mobile,email=email,code= otp_code,api_token=csrf,api_key=requestid,otp_tries=otp_tries,status=status,created_at=otp_send_date,otp_request_count=otp_request_count)
        db.session.add(new_otp)
        db.session.commit()
		#send otp
        LOG.debug("****%s:**** OTP is :%s******",requestid,otp_code) 
        
        ssl_otp_response=app.utils.send_sms_by_ssl(mobile,otp_msg)
		#lib.send_sms_by_ssl(mobile,'hello world')
        #print ("CSRF3 ")
		#print (csrf)
        #ssl_otp_response['trackingcode'] = requestid
        print ("ssl insert ")
        print (ssl_otp_response['status'])
        print(ssl_otp_response)
        add_ssl_otp(ssl_otp_response,requestid)

        jsdata = {'baseurl': current_app.config["BASE_URL"], 'bkash_api_url':  current_app.config["BKASH_API_URL"],'otp_expire_time':current_app.config["OTP_EXPIRE_TIME"],'trackingcode':requestid,'bkash_api_username':username,'bkash_api_password':password}
        print (jsdata)
        
        
        return render_template('otp.html', otp_send_date = view_otp_send_date,customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,
        csrf=csrf,message=msg,trackingcode=requestid,type=request_type,jsdata=jsdata)
        #print ('hello')
    except Exception as error:
        print (error)
        LOG.debug("***********Error :  %s ***********%s***",error,requestid)
        
        return jsonify({"message": f"OTP not generated"},{"status":" fail"})
        #return render_template('otp.html', otp_send_date = otp_send_date,customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf)
	
    else:
        #LOG.debug("*********** Tracking ID not send **************")
        LOG.warning("****Error  :  %s  tracking id not found ******",requestid)
        return jsonify({"message": f"OTP not generated"},{"status":" fail"})'''


@main.route("/resend/",methods = ['POST'])
def otp_resend():
    
    LOG.debug("*********************** OTP Resend Start ****************")
    
    if request.method == "POST":

        print ('resend call ')
        try:
            csrf = request.form['csrf_token']
            #session['session_csrf']   = csrf
            trackingcode = request.form['trackingcode']
            mtype = request.form['type']
            mobile = request.form['mobile_number']
            request_type = trackingcode[:2]
            LOG.debug("***********************Tracking Code : *********:%s*******",trackingcode)
            
            LOG.debug("***********************%s: ***** UserOTP Request ****:%s*******",trackingcode,request_type)
            LOG.debug("** Tracking COde  :%s,*OTP:%s,* Request Type****:%s*******",trackingcode,mobile,request_type)
            
            db_result_item = OTPModel.query.filter(OTPModel.mobile == mobile,OTPModel.api_key==trackingcode).order_by(OTPModel.id.desc()).first()
            LOG.debug("*****Check OTP Limit:***trackingcode:******:%s OTP Request:*****%s*",trackingcode,db_result_item.otp_request_count)
            print (db_result_item)
            
            if db_result_item:
                otp_limit_status,url = app.utils.checkOTPLimitExceed(trackingcode,current_app.config['MAX_OTP_LIMIT'],db_result_item.otp_request_count,current_app.config['BKASH_API_URL'],request_type)
                opt_limit_url = url
                
                if otp_limit_status: 
                    #opt_limit_url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
                    session.pop('trackingcode', None)
                    session.pop('session_csrf', None) 
                    return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"Maximum 3 times you can try . "})
            
                #LOG.debug("**Update DB Status ***********")
                #db_result_item.otp_request_count = db_result_item.otp_request_count + 1
                #db.session.commit()
            
            print('request')
            #csrf 	= request.form['csrf_token']
            print ('csrf ...')
            print (csrf)
            #if not csrf:
            #csrf =   generate_csrf()
            
            print ('here')
            otp_code 				  = app.utils.otpgen()
            print ("OTP CODE: " + otp_code)
            LOG.debug("*******%s:****************Re-Send OTP Code : *********:%s*******",trackingcode,otp_code)
            
            if request_type =="LN":
                msg = 'By Submitting OTP, You are agreeing to link AB Bank Account with bKash Account.'
                otp_msg = 'Dear Customer, Your OTP '+otp_code+ ' to link AB Bank Account with bKash Account. For any Query, call: 16207'
            else:
                msg = 'By submitting OTP you are agreeing to add money to bKash from AB Bank Account'
                otp_msg = 'Dear Customer, Your OTP '+otp_code+ ' to add money to bKash from AB Bank Account. For any Query, call: 16207'
            
            now                       = datetime.datetime.now()
            otp_send_date             = now.strftime("%Y-%m-%d %H:%M:%S")
            csmsid                    = random.randint(1, 99999999)
            dt 						  = datetime.datetime.now()
            id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            mobile 					  = mobile
            email 					  = 'no-reply@abbl.com'
            otp_tries 				  = db_result_item.otp_tries
            otp_request_count         = db_result_item.otp_request_count + 1 
            session['session_csrf']   = csrf
            status 					  = 0
            
            print (otp_code)
            new_otp = OTPModel(
                    id=id,
                    mobile = mobile,
                    email   =email,
                    code    = otp_code,
                    api_token = csrf,
                    api_key = trackingcode,
                    otp_tries = otp_tries,
                    status = status,
                    created_at = otp_send_date,
                    otp_request_count = otp_request_count
            )
            db.session.add(new_otp)
            db.session.commit() 
            
            #subject = 'your otp'
            #message = 'Your otp is ' + otp_code
            #app.utils.send_email_alert(subject,email,message,id)

            print ('successfully added')
            ssl_otp_response=app.utils.send_sms_by_ssl(mobile,otp_msg)
		    #lib.send_sms_by_ssl(mobile,'hello world')
            #print ("CSRF3 ")
		    #print (csrf)
            print ("ssl insert ")
            print (ssl_otp_response['status'])
            print(ssl_otp_response)
            add_ssl_otp(ssl_otp_response,trackingcode)


            return jsonify({"message": f"OTP  generated"},{"status":" success"})
        except Exception as error:

            print (error)
            LOG.debug("******* %s :****************OTP error Message : *******",error)
            return jsonify({"message": f"OTP not generated"},{"status":" fail"})

    else :

        LOG.debug("***********************OTP error Not POST METHOD *********")
        return jsonify({"message": f"OTP Not send"},{"satatus":" fail"})	




@main.route("/cancel/",methods = ['GET', 'POST'])
def otp_cancel():
    if request.method == "POST":
        try:
            csrf = request.form['csrf_token']
            trackingcode = request.form['trackingcode']
            mtype = request.form['type']
            request_type = trackingcode[:2]
            print ("CSRF : " + csrf)
            print ("tracking code: " +trackingcode)
            print ("request type  : "+request_type)
            LOG.debug("***********************%s: ***** User  OTP Cancel ***********",trackingcode)
            LOG.debug("** Tracking COde  :%s,* Request Type****:%s*******",trackingcode,request_type)
            if (request_type == 'LN'):
                resultCode = "B1103"
                #url = current_app.config['BKASH_API_URL']+'/account/link/redirect?id='+trackingcode+'&resultcode='+resultCode
                url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
            else : 
                resultCode = "B1405"
                #url = current_app.config['BKASH_API_URL']+'/add/money/redirect?id='+trackingcode+'&resultcode='+resultCode
                url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
            print ("return url : " + url)
            LOG.debug("***********************%s: ***** Redirect URL****:%s*******",trackingcode,url)
            session.pop('trackingcode', None)
            session.pop('session_csrf', None)
            return jsonify({"status":"success"},{"redirectUrl":url} )
        
        
        except Exception as error:
            print (error)




@main.route("/verify/<code>/<type>/",methods = ['GET', 'POST'])
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
            request_type = request.form['request_type']
            url = current_app.config["BASE_URL"]
            #print (url)
            #mtype = request.form['type']
            #request_type = trackingcode[:2]
            #print (request.form['action'])
            #print ("Code : "+code)
            #print ("CSRF : " + csrf)
            #print ("tracking code: " +trackingcode)
            #print ("request type  : "+request_type)
            LOG.debug("***********************%s: ***** User Input OTP ****:%s*******",trackingcode,code)
            LOG.debug("** Tracking COde  :%s,*OTP:%s,* CSRF****:%s*******",trackingcode,code,csrf)
            db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first()
            
            print ("db result item ... ")
            print (db_result_item)
            print (db_result_item.mobile)
            LOG.debug("** otpinfo :%s",db_result_item)
            LOG.debug("** db result :%s",db_result_item)
            LOG.debug("** db result api key :%s",db_result_item.api_key)
            now  = datetime.datetime.now()
            otp_send_date  = now.strftime("%Y-%m-%d %H:%M:%S")
            dt =  datetime.datetime.now()
            id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
            
            #print ("Code : "+db_result_item.code)0.
            #print ("mobile : " + db_result_item.mobile)
            #print ("tracking code: " +trackingcode)
            #print ("user otp  : "+code)
            #print ("send time  : "+otp_send_date)
            
            new_otp_history = OTP_HISTORY(id=id,mobile=db_result_item.mobile,code= db_result_item.code,user_otp=code,api_token=trackingcode,created_at=otp_send_date)
            db.session.add(new_otp_history)
            db.session.commit()
            
            
            #print (db_result_item)
            print ("OTP Tries :")
            print (db_result_item.otp_tries)            
            LOG.debug("***********************Check OTP Expired result*********:%s*******",trackingcode)
            otp_expired_status,url = app.utils.checkOTPExpired(trackingcode,db_result_item.created_at,current_app.config['OTP_EXPIRE_TIME'])
            
            #url = url + 'email/' + trackingcode
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
            print (jsonify(item.serialize))
            if item:
                LOG.debug("**Update DB Status ***********")
                item.otp_tries = item.otp_tries + 1
                item.status = 1
                db.session.commit()

                url = current_app.config["BASE_URL"]
                #url = url + 'email/' + trackingcode
                print ("initial return url : " + url)
                #CUSTINFO.query.filter()
                replyItem = SMSINFO.query.filter(SMSINFO.trackingcode == trackingcode).first()
                
                if replyItem.message == "Verify":
                    #url = replyItem.callback_url
                    #url  = url
                    url = url + 'email/' + trackingcode+'/'+request_type


                    return jsonify({"status":"success"},{"redirectUrl":url},item.serialize )
                    #return jsonify({"status":"warning"},{"resultCode":"abcustom"},{"message": f"OTP  {code} does not match. please try again."})        

                else:         
                    ''''if (request_type == 'LN'):
                        resultCode = "0000"
                        #url = current_app.config['BKASH_API_URL']+'/account/link/redirect?id='+trackingcode+'&resultcode='+resultCode
                        url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
                    else : 
                        resultCode = "0000"
                        #url = current_app.config['BKASH_API_URL']+'/add/money/redirect?id='+trackingcode+'&resultcode='+resultCode
                        url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
                    '''
                    
                    if (request_type == 'sms'):
                        url = url + 'email/' + trackingcode+'/'+request_type
                    else:
                        url = url+'home/'+ trackingcode+'/'
                    
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
                    
                    print ("ssl insert ")
                    print (response['status'])
                    add_ssl_otp(response,trackingcode)
                    print ("Success return url : " + url)
                    LOG.debug("***********************%s: ***Succuess Redirect URL****:%s*******",trackingcode,url)
                    item = CUSTINFO.query.filter(CUSTINFO.api_token == trackingcode).first()                    
                    if item:
                        LOG.debug("**Update DB Status ***********")
                        #item.otp_tries = item.otp_tries + 1
                        item.sms_verify_status = 1
                        db.session.commit()
                    
                    
                    session.pop('trackingcode', None)
                    session.pop('session_csrf', None)
                   
                    return jsonify({"status":"success"},{"redirectUrl":url},item.serialize )
            else:

                print ('increase tries')
                LOG.debug("*******Error : ****************%s: ***** OTP: ****:%s*** does not match.****",trackingcode,code)
                #db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first_or_404()
                db_result_item = OTPModel.query.filter(OTPModel.api_token == csrf,OTPModel.api_key==trackingcode).first_or_404()
                print ("OTP Tries in error :")
                print (db_result_item.otp_tries)
                db_result_item.otp_tries       = db_result_item.otp_tries + 1
                LOG.debug("***********************%s: ***** OTP TRies : ****:%s*******",trackingcode,db_result_item.otp_tries)
                db_result_item.status = 0
                db.session.commit()
                
                print ('check ')
                print ('db result....')
                print (db_result_item.otp_tries)

                if (db_result_item.otp_tries >=current_app.config['MAX_OTP_LIMIT']):
                    #otp_limit_status,url = app.utils.checkOTPLimitExceed(trackingcode,current_app.config['MAX_OTP_LIMIT'],db_result_item.otp_tries,current_app.config['BKASH_API_URL'],request_type)
                    #print (otp_limit_status)
                    #print (url)
                    #LOG.debug("***********************%s: ***** OTP TRies : ****:%s*******",trackingcode,db_result_item.otp_tries)
                    #session.pop('trackingcode', None)
                    #session.pop('session_csrf', None)
                    '''if (request_type == 'LN'):
                        resultCode = "B1102"
                        #url = current_app.config['BKASH_API_URL']+'/account/link/redirect?id='+trackingcode+'&resultcode='+resultCode
                        opt_limit_url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
                    else : 
                        resultCode = "B1404"
                        #url = current_app.config['BKASH_API_URL']+'/add/money/redirect?id='+trackingcode+'&resultcode='+resultCode
                        opt_limit_url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
                    '''
                    
                    return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"Maximum 3 times you can try . "})
                
                
                return jsonify({"status":"warning"},{"resultCode":"abcustom"},{"message": f"OTP  {code} does not match. please try again."})
                #print (item)
        except Exception as error:
            print (error)
            session.pop('trackingcode', None)
            session.pop('session_csrf', None)
            return jsonify({"message": f"Tracking code  not found"},{"status":" fail"})
    else:
        # only for test purpose
        items = OTPModel.query.filter((OTPModel.code == code)).first_or_404()
        print ("get ...")
        print (items)
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


def add_otp (mobile,email,code,api_token,api_key,otp_tries):

    id =  random.randint(10000000,99999999)
    mobile = '01673615825'
    email = 'thinker.bijon@gmail.com'
    code = '1234'
    api_token = '123456'
    api_key = '12345678'
    otp_tries = 1
    status = 1
    now=datetime.datetime.now()
    created_at =  now.strftime("%Y-%m-%d %H:%M:%S")

    new_otp = OTPModel(
                    id=id,
                    mobile = mobile,
                    email=email,
                    code = code,
                    api_token = api_token,
                    api_key = api_key,
                    otp_tries = otp_tries,
                    status = status,
                    created_at = created_at 
    )

    #db.session.add(new_otp)
    #db.session.commit()

def add_ssl_otp (response,reqid=''):
    
    try:
    
        dt 						  = datetime.datetime.now()
        id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
        print ("SMS INFO : ")
        print (response)

        
        print ("DB SMS INFO EXECUTED : ")
        code = response.get("code")

        print ("Code {code}")
        print (code)
        message = response.get("message")
        print (message)
        mobile = response.get("phone")
    
        rstatus = response.get("status")
        if rstatus == 'success':
            status = 1
        else : 
            status = 0
        
        sms_send_time = response.get("sms_send_time")
        reference_no =response.get("reference_no")
        return_url  =response.get("callback_url")
        if return_url:
            callback_url = response.get("callback_url")
        else:
            callback_url = ''    
        ssl_reply_message =response.get("ssl_reference_no")
        if reqid:
            trackingcode = reqid
        else:
            trackingcode = response.get("trackingcode")
        #ssl_sms_reply_status = response.get("ssl_sms_reply_status")
        ssl_sms_reply_status = response.get("result")
        now    = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S") 
        print ("Call db smsinfo ")
        print (ssl_reply_message)
        new_sms_info = SMSINFO(id=id,code=code,mobile=mobile,message=message,status=status,sms_send_time=sms_send_time,ssl_reply_message=ssl_reply_message,ssl_sms_reply_status=ssl_sms_reply_status,created_at=created_at,trackingcode=trackingcode,callback_url=callback_url)
        #new_sms_info = SMSINFO(id,code,mobile,message,status,sms_send_time,ssl_reply_message,ssl_sms_reply_status,created_at,trackingcode)
        #(self,id,code,mobile,message,status,sms_send_time,ssl_reply_message,ssl_sms_reply_status,created_at,trackingcode)
        print ("SMS INFO")
        print (new_sms_info)
        db.session.add(new_sms_info)
        db.session.commit()
        print ('db addedd')
    
    except Exception as error:
        print (error)
        LOG.debug("***********Error :  %s ***********%s***",error,response["trackingcode"])


@main.errorhandler(CSRFError)
def handle_csrf_error(e):
    #print ('error....')
    #print (e)
    #print (e.description)
    '''trackingcode =  session['trackingcode']
    request_type= trackingcode[:2]
    if (request_type == 'LN'):
        resultCode = "B1101"
        #url = current_app.config['BKASH_API_URL']+'/account/link/redirect?id='+trackingcode+'&resultcode='+resultCode
        url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
    else : 
        resultCode = "B1403"
        #url = current_app.config['BKASH_API_URL']+'/add/money/redirect?id='+trackingcode+'&resultcode='+resultCode
        url = app.utils.getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)

    return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"OTP page session expired.  "})'''

    return jsonify({"status":"fail"},{"message": f"OTP page session expired.  "})

    