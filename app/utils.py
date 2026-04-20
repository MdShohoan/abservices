import os
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
from sqlalchemy.orm.session import Session
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO,EQSessiontoken


from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from smtplib import SMTPException
from flask import  current_app

from app import db 
from app import LOG

from zeep import Client
from zeep.transports import Transport


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
    'clientAppId':'abeqservice',
    'system' :CBS_SYSTEM,
    'unit'	: CBS_UNIT,
    'user' :  CBS_USERNAME,
    'pass' : CBS_PASSWORD
}

def eqlogin():
    
    try:
        print (f"wsdl : {eqConnectwsdl}")
        client =Client(wsdl = eqConnectwsdl)
        print (f" connection request {request_cbs_login_data}")
        result =  client.service.login(**request_cbs_login_data)
        print (result)
        sessiontoken = result
        return sessiontoken
    
    except Exception as e:
        print (e)
        return False


def eqlogout(sessiontoken):
    client = Client(wsdl = eqConnectwsdl)
    result = client.service.logout (sessiontoken)
    return result



def getEQSessionToken():
    try:
        print (" Get Equation TOken : ")
        session_token = None
        is_new_login = False
        
        # Retrieve session token from DB
        eq_info = EQSessiontoken.query.first()
        print(f"DB session token info: {eq_info}")
        
        if eq_info is None or eq_info.eqsessiontoken == 'false':
            is_new_login = True
        else:
            session_token = eq_info.eqsessiontoken
            print(f" session token info: {session_token}")
            if not getConnectionStatus(session_token):
                print("Session token invalid, logging out and re-authenticating.")
                eqlogout(session_token)
                is_new_login = True
        
        if is_new_login:
            session_token = eqlogin()
            if session_token:
                if eq_info is None:
                    new_db_session_token = EQSessiontoken(id=1, eqsessiontoken=session_token)
                    db.session.add(new_db_session_token)
                else:
                    eq_info.eqsessiontoken = session_token
                db.session.commit()
                print(f"New session token stored: {session_token}")
        
        return session_token
    
    except SQLAlchemyError as db_err:
        print(f"Database error: {db_err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None



'''def getEQSessionToken():
    try:
        session_token = None
        is_new_login = False
        
        # Retrieve session token from DB
        eq_info = EQSessiontoken.query.first()
        #current_app.logger.debug(f"DB session token info: {eq_info}")
        print (f"DB session token info: {eq_info}")
        
        if eq_info is None or eq_info.eqsessiontoken == 'false':
            is_new_login = True
        else:
            session_token = eq_info.eqsessiontoken
            if not getConnectionStatus(session_token):
                #current_app.logger.debug("Session token invalid, logging out and re-authenticating.")
                eqlogout(session_token)
                is_new_login = True
        
        if is_new_login:
            session_token = eqlogin()
            if session_token:
                if eq_info is None:
                    new_db_session_token = EQSessiontoken(id=1, eqsessiontoken=session_token)
                    db.session.add(new_db_session_token)
                else:
                    eq_info.eqsessiontoken = session_token
                db.session.commit()
                #current_app.logger.debug(f"New session token stored: {session_token}")
                print (f"New session token stored: {session_token}")
        return session_token
    
    except SQLAlchemyError as db_err:
        #current_app.logger.error(f"Database error: {db_err}")
        print (f"atabase error: {db_err}")
        
        return None
    except Exception as e:
        #current_app.logger.error(f"Unexpected error: {e}")
        return None
'''


'''def getEQSessionToken():
    eqinfo = EQSessiontoken.query.first()
    print (' eqinfo : ')
    print (eqinfo)
    isNewLogin = False
    sessionToken = ''
    if eqinfo:
        sessionToken = eqinfo.eqsessiontoken
        print ("Session token ")
        print (sessionToken)
        if sessionToken is None :
            isNewLogin = True
        else:
            res = getConnectionStatus(sessionToken)
            if res:
                print ('Connection exist')
            else:
                eqlogout(sessionToken)
                #isNewLogin = True	
                sessionToken = eqlogin()
                eqinfo.eqsessiontoken = sessionToken
                db.session.commit()


    else:
        isNewLogin = True

    if isNewLogin :
        sessionToken = eqlogin()
        now    = datetime.datetime.now()
        created_at = now.strftime("%Y-%m-%d %H:%M:%S")
        id 						  = int(now.strftime("%Y%m%d%H%M%S%f")[:-3])
        newdbsessiontoken 		  = EQSessiontoken(id,sessionToken,created_at)
        db.session.add(newdbsessiontoken)
        db.session.commit()
    return sessionToken
'''
'''
def getConnectionStatus(sessionToken):
    
    try:
        data = {'sessionToken' : sessionToken}
        client = Client(wsdl = eqConnectwsdl)
        result =  client.service.getConnectionStatus(**data)
        print (result)
        if result == 'true':
            #sessiontoken = result
            return True
        else :
            return False
    except Exception as e:
        print (e)
        return False
'''

def getConnectionStatus(sessionToken):
	
	try:
		#temporary off for cbs api has no getConnectionStatus
		print (f" check token status {sessionToken}")
		data = {'sessionToken' : sessionToken}
		eqConnectwsdl = current_app.config['EQCONNECTWSDL']
		client = Client(wsdl = eqConnectwsdl)
		result =  client.service.getConnectionStatus(**data)
		print (f" equation connection {result}")
		if result :
			#sessiontoken = result
			return True
		else :
			return False
		#return True
	except Exception as e:
		print (e)
		return False

def customerEquationDetail(account_no):
    
    print (f"Enter customerEquationDetail ")
    sessiontoken = getEQSessionToken()
    print (f" session token is : {sessiontoken}")
    request_data = { 
                    'sessionToken' : sessiontoken,
                    'accno' : account_no,
                    'isEQAcc' : False
                }
    LOG.info('Account: %s: , Request Data : 1.session token : %s  ', account_no, sessiontoken)
    transactionClient = Client(eqEnqurywsdl)
    eqresult = transactionClient.service.customerEquationDetail(**request_data)
    print (f" customerEquationDetail : {eqresult}")
    LOG.info('Account: %s: , Custer Equation details Result Data : : %s  ', account_no, eqresult)
    return eqresult


def accountStatus(accno):

    accstatusresult = {}
    sessiontoken = getEQSessionToken()
    request_data = { 
                        'sessionToken' : sessiontoken,
                        'accno' : accno
                    }
    LOG.info('Account: %s: , Request Data for account status : 1.session token : %s ', internal_account, sessiontoken)
    accstatusresult = transactionClient.service.accountStatus(**request_data)
    if accstatusresult['success'] == True :
        blocked = accstatusresult['blocked']
        closing = accstatusresult['closing']
        inactive = accstatusresult['inactive']
        decOrLiq = accstatusresult['decOrLiq']
        if inactive == False:
            return False

    return True



def customerDetails(custno):

    cusresult = {}
    
    try:
        sessiontoken = getEQSessionToken()
        request_data = { 
                        'sessionToken' : sessiontoken,
                        'custno' : custno
                    }
        LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
        transactionClient = Client(eqEnqurywsdl)
        cusresult = transactionClient.service.customerDetails(**request_data)
        LOG.info('Account: %s: , Cust details Result Data : : %s  ', custno, cusresult)

    except Exception as error:
        print (error)
        LOG.debug("***********Error :  %s ***********%s***",error,custno)

    return cusresult

def addCustomerDetails(custMnem,custLoc,email):

    api_response = False
    empty_none_value = None
    try:
        sessiontoken = getEQSessionToken()
        LOG.info('Account: %s: , session token : %s  ', custMnem, sessiontoken)
        transactionClient = Client(eqTransactionwsdl)
        request_data = { 
            'sessionToken' : sessiontoken,
            'custMnem' : custMnem,
            'custLoc' :  "",
            'email1' : email
        }
        cusresult = transactionClient.service.addCustomerDetails(**request_data)
        LOG.info('Account: %s: , Cust details Result Data : : %s  ',custMnem, cusresult)
        #print (cusresult)
        #print ('Email Update ok')
        return  cusresult['success']
    except Exception as error:
        print (error)
        LOG.debug("***********Error :  %s ***********%s***",error,custMnem)
        return api_response



    

def add_ssl_otp (response,reqid=''):
    
    try:
    
        dt 						  = datetime.datetime.now()
        id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
        #print ("SMS INFO : ")
        #print (response)

        
        #print ("DB SMS INFO EXECUTED : ")
        # code = response.get("code")
        code = response.get("code") or response.get("ssl_reference_no") or 'DEV'

        #print ("Code {code}")
        #print (code)
        message = response.get("message")
        #print (message)
        mobile = response.get("phone")
    
        rstatus = response.get("status")
        if rstatus == 'success':
            status = 1
        else : 
            status = 0
        
        # sms_send_time = response.get("sms_send_time")
        sms_send_time = datetime.datetime.now()
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
        #print ("Call db smsinfo ")
        #print (ssl_reply_message)
        new_sms_info = SMSINFO(id=id,code=code,mobile=mobile,message=message,status=status,sms_send_time=sms_send_time,ssl_reply_message=ssl_reply_message,ssl_sms_reply_status=ssl_sms_reply_status,created_at=created_at,trackingcode=trackingcode,callback_url=callback_url)
        #new_sms_info = SMSINFO(id,code,mobile,message,status,sms_send_time,ssl_reply_message,ssl_sms_reply_status,created_at,trackingcode)
        #(self,id,code,mobile,message,status,sms_send_time,ssl_reply_message,ssl_sms_reply_status,created_at,trackingcode)
        #print ("SMS INFO")
        #print (new_sms_info)
        db.session.add(new_sms_info)
        db.session.commit()
        #print ('db addedd')
    
    except Exception as error:
        print (error)
        LOG.debug("***********Error :  %s ***********%s***",error,response["trackingcode"])

def send_otp (account_no,customer_data,request_type) :
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
    
    email = customer_data.get('email')
    if not mobile and email is None:
        return False,ssl_otp_response 
    
    otp_code                 = otpgen()
    if mobile:
        unmasked                 = str(account_no)
        masked_account_number    = unmasked[0:3]+len(unmasked[:-8])*"*"+unmasked[-4:]
        masked_mobile            = mobile[-3:].rjust(len(mobile), "*")
        
        if request_type == 'formc':
            otp_msg                  = 'DO NOT DISCLOSE YOUR OTP TO ANYONE. Your OTP is '+otp_code+ ' to fillup your formc. This OTP will expire in 3 minutes. For any Query call 16207'
        else:
            otp_msg                  = 'DO NOT DISCLOSE YOUR OTP TO ANYONE. Your OTP is '+otp_code+ ' to update your email This OTP will expire in 3 minutes. For any Query call 16207'




    '''if not mobile:
        mobile = '01673615816'
    '''
    csrf                     = customer_data.get('csrf')
    email                    = customer_data.get('email')
    if  email is not None:
    
        #otp_code                 = otpgen()
        if request_type == 'formc':
            otp_msg                  = 'DO NOT DISCLOSE YOUR OTP TO ANYONE. Your OTP is '+otp_code+ ' to fillup your formc. This OTP will expire in 3 minutes. For any Query call 16207'
        else:
            otp_msg                  = 'DO NOT DISCLOSE YOUR OTP TO ANYONE. Your OTP is '+otp_code+ ' to update your email This OTP will expire in 3 minutes. For any Query call 16207'
    else:
        email = 'no-reply@abbl.com'

    
    
    
    csmsid                   = random.randint(1, 99999999)
    
    #otp_code                 = otpgen()
    #otp_msg                  = 'Dear Customer, Your One-Time Password is '+otp_code+ '.Please use this OTP to complete the Email Update.For any Query, call: 16207'
    #otp_msg                  = 'DO NOT DISCLOSE YOUR OTP TO ANYONE. Your OTP is '+otp_code+ ' to update your email This OTP will expire in 3 minutes. For any Query call 16207'
    id= requestid 
    #sms_send (phone,message,id)
    try:
        new_otp = OTPModel(id=id,mobile=mobile,email=email,code= otp_code,api_token=csrf,api_key=requestid,otp_tries=otp_tries,status=verify_status,created_at=otp_send_date,otp_request_count=otp_request_count)
        db.session.add(new_otp)
        db.session.commit()
        print ('**********otp insert*******')
        #send otp
        LOG.debug("****%s:**** OTP is :%s******",requestid,otp_code) 
        
        #ssl_otp_response=app.utils.send_sms_by_ssl(mobile,otp_msg)
        #print ('before sms api call...')
        #print (f'mobile : {mobile}')
        if mobile:
            # ---- DEV MODE: skip SMS, return success directly ----
            print(f"====== DEV MODE OTP ======")
            print(f"Mobile : {mobile}")
            print(f"OTP    : {otp_code}")
            print(f"==========================")
            
            view_otp_send_date = now.strftime("%Y-%m-%d %H:%M:%S")
            ssl_otp_response = {
                'status'                : 'SUCCESS',
                'result'                : 'dev mode',
                'phone'                 : mobile,
                'sms_type'              : 'EN',
                'message'               : otp_msg,
                'reference_no'          : 'DEV123',
                'ssl_reference_no'      : 'DEV123',
                'sms_send_time'         : datetime.datetime.now(),  # <-- datetime object not string
                'ssl_reply_message'     : 'Verify',
                'trackingcode'          : requestid,
                'datetime'              : now.strftime("%Y-%m-%d %H:%M:%S"),  # <-- fix format
                'callback_url'          : '',
                'view_otp_send_date'    : now.strftime("%d-%m-%Y %H:%M:%S"),  # display format is ok
                'customer_mask_mobile'  : masked_mobile,
                'customer_account_number': masked_account_number,
                'customer_name'         : customer_name,
                'statement_path'        : ''
            }
            add_ssl_otp(ssl_otp_response, requestid)
            return True, ssl_otp_response        
        # if mobile:
        #     #print (f'mobile : {mobile}')
        #     ssl_otp_response=smsnewapi(mobile,otp_msg)
        #     #print ('after sms api call...')
        #     #print (ssl_otp_response)
        #     if ssl_otp_response.get('status') == 'SUCCESS':
        #         add_ssl_otp(ssl_otp_response,requestid)
        #         view_otp_send_date            = now.strftime("%d-%m-%Y %H:%M:%S")
        #         #print (view_otp_send_date)
        #         #return render_template('otp.html', otp_send_date = view_otp_send_date,customer_mask_mobile=masked_mobile,mobile=mobile,customer_name=customer_name,customer_account_number=masked_account_number,csrf=csrf,message=otp_msg,trackingcode=requestid)
        #         ssl_otp_response.update({'view_otp_send_date': view_otp_send_date,
        #                              'customer_mask_mobile':masked_mobile,
        #                              'mobile' : mobile, 
        #                              'customer_account_number' :masked_account_number,
        #                              'customer_name' : customer_name,
        #                              'statement_path':''    
        #                              })
                              
        #         #print (ssl_otp_response)
        #         return True,ssl_otp_response
        #     else : 
        #         return False,ssl_otp_response    
        else:
            
            if email is not None and email !='no-reply@abbl.com':
                url = ''
                send_email_alert(mobile,otp_msg)
                ssl_otp_response = {
                    'status'                : 'SUCCESS',
                    'result'                : 'dev mode',
                    'phone'                 : mobile,
                    'sms_type'              : 'EN',
                    'message'               : otp_msg,
                    'reference_no'          : 'DEV123',
                    'ssl_reference_no'      : 'DEV123',
                    'sms_send_time'         : datetime.datetime.now(),  # <-- datetime object not string
                    'ssl_reply_message'     : 'Verify',
                    'trackingcode'          : requestid,
                    'datetime'              : now.strftime("%Y-%m-%d %H:%M:%S"),  # <-- fix format
                    'callback_url'          : '',
                    'view_otp_send_date'    : now.strftime("%d-%m-%Y %H:%M:%S"),  # display format is ok
                    'customer_mask_mobile'  : masked_mobile,
                    'customer_account_number': masked_account_number,
                    'customer_name'         : customer_name,
                    'statement_path'        : ''
                }

            
            
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
        print ('error:')
        print (e) 
        return False,ssl_otp_response




def  do_account_verifiy (requestid, account_no,csrf='') :

    try:
        #print ("enter acount verify : ")
        customer_found = False
        custno = ''
        session = Session ()
        session.verify = False
        address = ''
        
        ssl_otp_response = {}
        customer_data = {}
        LOG.info("******* Api call api ,  : %s Requestid  :%s*******",account_no,requestid)
        
        '''client =Client(wsdl = eqConnectwsdl)
        print (client)
        print ('API CALL..')'''
        #print (" acount verify : " + account_no)
        if account_no: 
            
            LOG.info("******* Api call for account 2 :%s*******",account_no)
            #custno = account_no[4:-3]
            #custno = account_no
            #print ('customer')
            #print (custno)
            LOG.info("******* Account :%s*****customer : %s**",account_no,account_no)
            
            #sessiontoken =  client.service.login(**request_cbs_login_data)
            sessiontoken = getEQSessionToken()
            print (f"sesstion token is : " +sessiontoken)
            if sessiontoken :     
                    LOG.info('Account: %s: , session token : %s  ', account_no, sessiontoken)
                    transactionClient = Client(eqEnqurywsdl)

                    request_data = { 
                        'sessionToken' : sessiontoken,
                        'accno' : account_no,
                        'isEQAcc' : False
                    }
                    
                    LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
                    eqresult = transactionClient.service.customerEquationDetail(**request_data)
                    LOG.info('Account: %s: , Custer Equation details Result Data : : %s  ', account_no, eqresult)
                    #print (eqresult)
                    if eqresult['success'] == True:
                        custno = eqresult['customerId']
                        internal_account = eqresult['eqAccount']
                        external_account = eqresult['externalAccount']
                        
                        branch_code = internal_account[0:4]
                        print (branch_code)
                        LOG.info('Account: %s: , Custer Equation Bracn Code : : : %s  ', account_no, branch_code)
                    if not custno:
                        return customer_found,customer_data 
                    
                    request_data = { 
                        'sessionToken' : sessiontoken,
                        'accno' : external_account
                    }
                    
                    LOG.info('Account: %s: , Request Data for account status : 1.session token : %s ', internal_account, sessiontoken)
                    accstatusresult = transactionClient.service.accountStatus(**request_data)
                    #print ("accountStatusResult api result  : ")
                    #print (accstatusresult)
                    if accstatusresult['success'] == True :
                        #print ('enter 3rd api call : ')
                        blocked = accstatusresult['blocked']
                        closing = accstatusresult['closing']
                        inactive = accstatusresult['inactive']
                        decOrLiq = accstatusresult['decOrLiq']
                        #print ( inactive)

                        if inactive == True:
                            return customer_found,customer_data
                        
                        #LOG.info('Account: %s: , Request Data : 1.session token : %s  ', custno, sessiontoken)
                        #cusresult = transactionClient.service.accountStatus(**request_data)
                        request_data = { 
                            'sessionToken': sessiontoken,
                            'custno': custno
                        }

                        # ✅ ADD THESE DEBUG LINES
                        print("===== DEBUG customerDetails =====")
                        print("sessionToken:", sessiontoken)
                        print("custno:", custno)
                        print("Request Data:", request_data)

                        # OPTIONAL: check method signature
                        print("Method signature:", transactionClient.service.customerDetails)

                        print('customer details api call : ')

                        cusresult = transactionClient.service.customerDetails(**request_data)

                        # ✅ PRINT FULL RESPONSE
                        import json
                        print("Full Response:", json.dumps(cusresult, indent=2, default=str))
                        print("================================")
                        LOG.info('Account: %s: , Cust details Result Data : : %s  ', custno, cusresult)
                        print ('customer details api result  : ')
                        print (cusresult)
                        if cusresult['success'] == True : 
                            customer_name = cusresult['customerName']
                            email1 = cusresult['email1']
                            if not cusresult['mobile']:
                                mobile = ''
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

                            request_data = { 
                            'sessionToken' : sessiontoken,
                            'forCustomer' : True,
                            'addressType' : "",
                            'custMnemonic':custno,
                            'custLocation':""
                            }
                        
                            LOG.info('Account: %s: , Request Data : Address : %s  ', custno, sessiontoken)
                            addressresult = transactionClient.service.addressEnquiry(**request_data)
                            print ('Address Result: ')
                            print (addressresult)
                            if addressresult['success'] == True :
                                addrLine1 = addressresult['addrLine1']
                                addrLine2 = addressresult['addrLine2']
                                addrLine3 = addressresult['addrLine3']
                                addrLine4 = addressresult['addrLine4']
                                addrLine5 = addressresult['addrLine5']
                                custaddress = [addrLine1,addrLine2,addrLine3,addrLine4,addrLine5]
                                address = ' '.join(filter(None,custaddress))
                                #address = str(addrLine1) + " " +str(addrLine2)+" "+str(addrLine3)+" "+str(addrLine4)+" "+str(addrLine5)
                        
                        
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
                                            'branch_code' : branch_code,
                                            'internal_account': internal_account,
                                            'external_account':external_account,
                                            'address':address
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
                                    customer_data = {}
                                    LOG.error("Account: %s: Error  %s",account_no, e) 
                                    return customer_found,customer_data
                            

                    else : 
                        LOG.error("Account: %s: API  output  %s",account_no, sessiontoken) 
                        
                    
                    #result = client.service.logout (sessiontoken)
                    #LOG.debug('Account: %s: , Logout Result Data : : %s  ', custno, result)
                    return customer_found,customer_data
            else:
                print ('Account Login Info: ')
                return customer_found,customer_data 

        else:
            LOG.info("******* Account :%s*****Cannot be blank : %s**",account_no)
            return customer_found,customer_data   

    except Exception as e:
        print (e)
        LOG.error("Account: %s: Error  %s",account_no, e) 
        return customer_found,customer_data

def update_tin_cbs(requestid,tin_no,financial_year,custMnem):
    
    api_response = False
    empty_none_value = ''
        
    try:
       
        LOG.info("******* Api call api ,  : %s Requestid  :%s*******",requestid,tin_no)
        client =Client(wsdl = eqConnectwsdl)
        LOG.info("******* Account :%s*****customer : %s**",requestid,tin_no)
        sessiontoken =  client.service.login(**request_cbs_login_data)
        if sessiontoken :     
            LOG.info('Account: %s: , session token : %s  ', requestid, sessiontoken)
            transactionClient = Client(eqTransactionwsdl)
            taxid_financial_year = tin_no + ' (' +financial_year+ ')'
            
            request_data = { 
                'sessionToken' : sessiontoken,
                'custMnem' : custMnem,
                'custLoc' :  "",
                'taxId' : taxid_financial_year
                

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



def otpErroUrl (request_type,bkash_api_url,trackingcode):
    url = '/'
  
  
    return status,url 


def checkOTPLimitExceed(trackingcode,MAX_OTP_LIMIT,otp_tries,):
    
    print ('otp limit check ')
    url = ''
    status = 0
    if otp_tries >=MAX_OTP_LIMIT : 
        #redirect_url = url + 
        status = 1 
        url = '/'
        LOG.debug("***************Error:********%s: ***** ****Maximum 3 times you can try .",trackingcode)
      
     
    print ('otp limit : return : ')
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
        url = '/'
        
        #LOG.debug("***********************%s: ***** Error OTP Time Expired:****:%s*******",trackingcode,dd.seconds)
    
        LOG.debug("***********************%s: ***** Error OTP Time Expired:****:%s*****Status:%s**",trackingcode,dd.seconds,status)

    return status,url    
        

def getRedirectUrl(bkash_url,request_type,resultCode,trackingcode):
    url = '/'
    return url
    
    

     
        


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
    current_file = os.path.abspath(os.path.dirname(__file__))
    email_filename = os.path.join(current_file, '../email_template.txt')
    print (email_filename)
    
    try:
        
        msg = MIMEMultipart() 
        # storing the senders email address 
        msg['From'] = sender 
        # storing the receivers email address 
        msg['To'] =  ", ".join(receivers)  
        # storing the subject 
        #msg['Subject'] = "Test Email with attachment"
        msg['Subject'] = subject
        #body = read_template('email_template.txt',message)
        body = read_template(email_filename,message)
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

def smsnewapi(mobile,otp_message=''):
    
    print ('.....new sms api call.....')
    response = {}
    uid = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    API_TOKEN = 'vfviysck-mepid5xf-kywkqoim-d59wman8-bv6japky'
    url = "https://smsplus.sslwireless.com/api/v3/send-sms"
    SID = 'ABBLDISPUTE'
    #API_TOKEN = current_app.config['SMM_API_TOKEN_V3']
    #url = current_app.config['SMS_API_URL_V3']
    #SID = current_app.config['SMS_API_SID_v3']
    
    MSISDN = mobile
    SMS = otp_message
    CMS_ID = uid
    #print (url)
    #print (CMS_ID)
    print (f"SMS"+SMS)
    #print (SMS)
    data = {'api_token': API_TOKEN, 'sid': SID, 'msisdn': MSISDN, 'sms':SMS,'csms_id':CMS_ID}
    json_data = json.dumps(data,ensure_ascii=False).encode('utf8')
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    
    '''response = {
                    'status': 'success',
                    'result': 'sms sent',
                    'phone': mobile,
                    'sms_type':'EN',
                    'message':otp_message,
                    'reference_no': '20221228121910',
                    'ssl_reference_no': '63abdfbbac066093890',
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }'''
    
    #return response
    r = requests.post(url, data=json_data, headers=headers)
    #Status Code: 200, Response: {'status': 'SUCCESS', 'status_code': 200, 'error_message': '', 'smsinfo': [{'sms_status': 'SUCCESS', 'status_message': 'Success', 'msisdn': '8801673615816', 'sms_type': 'BN', 'sms_body': 'আমার সোনার বাংলা', 'csms_id': '20221228121910', 'reference_id': '63abdfbbac066093890'}]}
    #print(f"Status Code: {r.status_code}, Response: {r.json()}")
    json_resp_data = r.json()
    print (json_resp_data)
    #json_resp_data = {'status': 'SUCCESS', 'status_code': 200, 'error_message': '', 'smsinfo': [{'sms_status': 'SUCCESS', 'status_message': 'Success', 'msisdn': '8801673615816', 'sms_type': 'BN', 'sms_body': 'আমার সোনার বাংলা', 'csms_id': '20221228121910', 'reference_id': '63abdfbbac066093890'}]}
    #LOG.debug("*******%s :  SMS SSL API Response  : %s  *******",mobile,json_resp_data)
    #return response
    
    #print (json_resp_data['status'])
    #print (json_resp_data['status_code'])
    #print (json_resp_data['error_message'])
    #print (json_resp_data['smsinfo'])
    #print (json_resp_data['smsinfo'][0]['sms_body'])
    #print (json_resp_data['smsinfo'])
    if (json_resp_data['smsinfo']):
        #print ('Hello World !')
        #print (json_resp_data['smsinfo'][0]['sms_body'])
        response = {
                    'status': json_resp_data['smsinfo'][0]['sms_status'],
                    'result': 'sms sent',
                    'phone': json_resp_data['smsinfo'][0]['msisdn'],
                    'sms_type':json_resp_data['smsinfo'][0]['sms_type'],
                    'message':json_resp_data['smsinfo'][0]['sms_body'],
                    'reference_no': json_resp_data['smsinfo'][0]['csms_id'],
                    'ssl_reference_no': json_resp_data['smsinfo'][0]['reference_id'],
                    'datetime': datetime.datetime.now().strftime('%Y-%m-%d %I:%M%p')
                }

    print (response)
    return response





