import requests
import csv
import math
import logging
import datetime
import xlsxwriter
import json
import random
import xmltodict
import smtplib


from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from smtplib import SMTPException
from flask import  current_app

from app import db 
from app import LOG


def otpErroUrl (request_type,bkash_api_url,trackingcode):
    url = ''
    status = 0
    if request_type == 'LN':
        resultCode = "B1102"
    else:
        resultCode = "B1404"
    
    url = getRedirectUrl(bkash_api_url,request_type,resultCode,trackingcode)
    return status,url 


def checkOTPLimitExceed(trackingcode,MAX_OTP_LIMIT,otp_tries,):
    
    url = ''
    status = 0
    if otp_tries >=MAX_OTP_LIMIT : 
        #redirect_url = url + 
        status = 1 
        LOG.debug("***************Error:********%s: ***** ****Maximum 3 times you can try .",trackingcode)
        '''if (request_type == 'LN'):
            resultCode = "B1102"
        else:
            resultCode = "B1404"
        '''
        #url = getRedirectUrl(bkash_api_url,request_type,resultCode,trackingcode)
    
    return status,url 
    #return jsonify({"status":"fail"},{"redirectUrl":url},{"message": f"Maximum 3 times you can try . "})

def checkOTPExpired(trackingcode,otp_send_time,OTP_EXPIRE_TIME):
    status                  = 0
    url                     = ''
    
    now                     = datetime.datetime.now()
    current_time            = now.strftime("%Y-%m-%d %H:%M:%S")
    time_format             = "%Y-%m-%d %H:%M:%S"
    
    dt1                     = otp_send_time
    dt2                     = datetime.datetime.strptime(current_time, time_format)
    dd                      = dt2 - dt1
    
    LOG.debug("***********************%s: ***** Time Difference:****:%s*******",trackingcode,dd.seconds)
    
    if (dd.seconds > OTP_EXPIRE_TIME):
        
        status = 1 
        
        #LOG.debug("***********************%s: ***** Error OTP Time Expired:****:%s*******",trackingcode,dd.seconds)
        '''if (request_type == 'LN'):
            resultCode = "B1101"
            #url = current_app.config['BKASH_API_URL']+'account/link/redirect?id='+trackingcode+'&resultcode='+resultCode
            url = getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
        else : 
            resultCode = "B1403"
            #url = current_app.config['BKASH_API_URL']+'add/money/redirect?id='+trackingcode+'&resultcode='+resultCode
            url = getRedirectUrl(current_app.config['BKASH_API_URL'],request_type,resultCode,trackingcode)
        '''

        LOG.debug("***********************%s: ***** Error OTP Time Expired:****:%s*****Status:%s**",trackingcode,dd.seconds,status)

    return status,url    
        

def getRedirectUrl(bkash_url,request_type,resultCode,trackingcode):
    
    
    """
    
        /** Mapping link account redirect result codes & description **/

            0000 - Link Created Successfully

            B1101 - OTP Session Expired

            B1102 - OTP Limit Exceed

            B1103 - OTP cancelled

        /** Mapping add money redirect error codes & description **/

            0000 - Transaction Completed

            B1403 - OTP Session Expired

            B1404 - OTP Limit Exceed

            B1405 - OTP cancelled

        * LN = Link Request

        * DL = De Link Request

        * QL = Query Link Status

        * AM = Add Money Request

        * AC = Add Money Cancel

        * QA = Query Add Money Status

        * TM = Transfer Money Request

        * QT = Query Transfer Money Status

    """
    
    response_bkash = { 
        
                        'LN': {  
                                '0000': 'Link Created Successfully',
                                'B1101': 'OTP Session Expired', 
                                'B1102': 'OTP Limit Exceed', 
                                'B1103': 'OTP cancelled'

                             },

                        'AM': {
                           
                                '0000': 'Transaction Completed',
                                'B1403': 'OTP Session Expired', 
                                'B1404': 'OTP Limit Exceed', 
                                'B1405': 'OTP cancelled'

                       
                        }
                    }
    
    message = response_bkash[request_type][resultCode]
    
    bkash_api_url = current_app.config['BKASH_API_URL']+'/info'
    username = current_app.config['BKASH_API_USERNAME']
    password = current_app.config['BKASH_API_PASSWORD']
    headers = {"charset": "utf-8", "Content-Type": "application/json","Username":username,"Password":password}
    
    
    create_row_data = {"id":trackingcode,"resultCode" : resultCode}
    
    
    

    url = ''
    if (request_type == 'LN'):
        
        url = bkash_url+'/account/link/redirect'
    else : 
        
        url = bkash_url+'/add/money/redirect'
    
    LOG.debug("******* API call for  :%s** url : **%s***",trackingcode,url )
    LOG.debug("******* API call for  :%s** paramaeter : **%s***",trackingcode,create_row_data )
    
    r = requests.post(url=url,auth=(username,password), json=create_row_data,headers=headers)
    LOG.debug("******* API Response for   :%s** url : **%s***",trackingcode,r.status_code )

       
    if r.status_code == 200 :
            records = json.loads(r.text)
            url = records["url"]
    
    return url
    
    '''
    
    if (request_type == 'LN'):
        
        url = bkash_url+'/account/link/redirect?id='+trackingcode+'&resultCode='+resultCode
    else : 
        
        url = bkash_url+'/add/money/redirect?id='+trackingcode+'&resultCode='+resultCode
    
    
    #print (message)
    return url
    '''

     
        


#from app import app
def otpgen():
    otp=""
    for i in range(6):
        otp+=str(random.randint(1,9))
    print ("Your One Time Password is ")
    print (otp)
    return otp

def otp_generate():
    #return "Hello, This is home page."
    #items = OTPModel.query.all()
    #print (items)
    #return render_template('index.html')
    message = ''
    if request.method == 'POST':
        mobile = request.form.get('mobile')  # access the data inside
        email = request.form.get('email')
        '''if username == 'root' and password == 'pass':
            message = "Correct username and password"
        else:
            message = "Wrong username or password"
        '''

def send_sms_by_ssl (phone,message):
#def send_sms_by_ssl (phone,message,id,mydb,cursor):

    LOG.debug ('SSL  :%s Request %s message : ' ,phone,message)
    print ('SMS Send SSL enter : ')
    #bkash_api_url = current_app.config['BKASH_API_URL']
    #print (bkash_api_url)
    #bkash_api_url = app.config['BKASH_API_URL']
    url = current_app.config['SMS_API_URL']
    
    print (url)
    #'http://192.168.113.108:8080/sms/'
    #http://192.168.253.2/pushapi/dynamic/server.php?user=abbl&pass=password&sid=abbankbulk&msisdn=01977123456&sms=&csmsid=298154290
    #
    #username = 'test'
    #password ='c<44H075'
    username =  current_app.config['SMS_USERNAME']
    #ABBANKBKASH'
    #password ='g=76H915'
    password =  current_app.config['SMS_PASSWORD']
    sid = current_app.config['SMS_SID']
    #sid = 'ABBLRetailLoan'
    # test purpose
    #phone ='8801673615816'
    #phone =str('8801779253539')
    #najmul vai 
    #phone =str('8801730097978')
    #tanjila 
    #phone =str('8801675086724')
    #message = 'This is a test '
    #message = 'Your AB Bank  has been debited TK 2,0000.!'
    csmsid = random.randint(1, 99999999)
    decode_response =False
    jsonResponse =''

    try:
        
        sslurl = url+'?msisdn='+phone+'&sms='+message+'&user='+username+'&pass='+password+'&sid='+sid+'&csmsid='+str(csmsid)
        print ('SMS SSL URL :' + sslurl)
        LOG.debug ('SSL URL : Request %s',sslurl)
        result = requests.get(sslurl)
        parsed_result = xmltodict.parse(result.text)
        print (result.text)
        LOG.debug("****%s:**** OTP response :%s******",phone,result.text) 
        if 'SMSINFO' in parsed_result['REPLY']:
            
            if 'REFERENCEID' in parsed_result['REPLY']['SMSINFO']:
                response = {
                    'status': 'success',
                    'result': 'sms sent',
                    'phone': phone,
                    'message': message,
                    'reference_no': parsed_result['REPLY']['SMSINFO']['CSMSID'],
                    'ssl_reference_no': parsed_result['REPLY']['SMSINFO']['REFERENCEID'],
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }
                
                ssl_reference_no = parsed_result['REPLY']['SMSINFO']['REFERENCEID']
                sms_reference_no = parsed_result['REPLY']['SMSINFO']['CSMSID']
                
                print ("ssl reference no: ")
                print (ssl_reference_no)
                jsonResponse = json.dumps(response)
                #update_sending_status(mydb,cursor,id)
                #update_sms_sending_status(mydb,cursor,id,sms_reference_no,ssl_reference_no)

            elif 'SMSVALUE' in parsed_result['REPLY']['SMSINFO']:
                response = {
                    'status': 'failed',
                    'result': 'invalid mobile or text',
                    'phone': phone,
                    'message': message,
                    'reference_no': '',
                    'ssl_reference_no': '',
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }
                print (" SMS Error : ")
                
                jsonResponse = json.dumps(response)

            elif 'MSISDNSTATUS' in parsed_result['REPLY']['SMSINFO']:
                response = {
                    'status': 'failed',
                    'result': 'invalid mobile',
                    'phone': phone,
                    'message': message,
                    'reference_no': '',
                    'ssl_reference_no': '',
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }
                print (" SMS Error : ")
                jsonResponse = json.dumps(response)
                
            elif 'PARAMETER' in parsed_result['REPLY']['SMSINFO']:
                response = {
                    'status': 'failed',
                    'result': 'All PARAMETERS ARE NOT EXISTS',
                    'phone': phone,
                    'message': message,
                    'reference_no': '',
                    'ssl_reference_no': '',
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }
                print (response)
                jsonResponse = json.dumps(response)
                    
            else:
                response = {
                        'status': 'failed',
                        'result': 'invalid credentials',
                        'phone': phone,
                        'message': message,
                        'reference_no': '',
                        'ssl_reference_no': '',
                        'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                    }
                
                jsonResponse = json.dumps(response)

           


        
        
        #if jsonData['status'] == "success" :
            #print (jsonData)
            #print ("update record")
    
        
    
    except Exception as e:
         print(e) 

    finally:
        print (jsonResponse)
        #if jsonResponse['status'] == "success" :
            #print (" Success ")
            #update_sending_status(mydb,cursor,id)
        #return jsonResponse
        return response

def send_email_alert (alert_type,email,message,id) :

    #sender = 'noreply@abbl.com'
    print (email)
    #email = ['saidur@abbl.com']
    sender = 'donotreply@abbl.com'
    #email = ['najmul@abbl.com', 'tkhanum@abbl.com','saidur@abbl.com']
    #receivers = ['najmul@abbl.com', 'tkhanum@abbl.com','saidur@abbl.com']
    #receivers = ['saidur@abbl.com']
    receivers = [email]
    #receivers = email
    subject = "ABBL Internet Banking - On-Demand Tokencode" + alert_type
    print ("subject:")
    print (subject)
    
    try:
        
        msg = MIMEMultipart() 
        # storing the senders email address 
        msg['From'] = sender 
        # storing the receivers email address 
        msg['To'] =  ", ".join(receivers)  
        # storing the subject 
        #msg['Subject'] = "Test Email with attachment"
        msg['Subject'] = subject
        body = read_template('email_template.txt',message)
        #print (body)

        msg.attach(MIMEText(body, 'plain'))
        text = msg.as_string() 
        smtpObj = smtplib.SMTP('mail.abbl.com', 25)
        #smtpObj = smtplib.SMTP('localhost')
        if (email):
            res = smtpObj.sendmail(sender, receivers, text)
            #update_sending_status(mydb,cursor,id)    
            print (res)
            print ("Successfully sent email")

    
    except SMTPException as e:
        print (e)
        print ("Error: unable to send email")


def add_email_info():
    
    print ('test')
    '''new_otp = SMSINFO(
					id=id,
					mobile = mobile,
					email   =email,
					code    = otp_code,
					api_token = csrf,
					api_key = csrf,
					otp_tries = otp_tries,
					status = status,
					created_at = otp_send_date 
	)'''
	#db.session.add(new_otp)
	#db.session.commit() 


def update_sending_status():
    
    print ('status')
    #item = OTPModel.query.filter(OTPModel.api_token == csrf).first()
    #if item:
        #item.otp_tries = item.otp_tries + 1
		#item.status = 1
		#db.session.commit()



def read_template(filename,alert_message):
    
    if (filename):
        with open(filename, "rb") as f:
            charset = 'utf-8'
            text = f.read().decode(charset).replace('{alert_message}',alert_message)
        
        return text


def save_log():
    #logging.basicConfig(filename='demo.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
    app.logger.info('Info level log')
    app.logger.warning('Warning level log')