from app import current_app,db
import urllib
import datetime
from pprint import pprint
import logging
import ldap3
from zeep import Client
import logging
import app.utils

from flask import Blueprint,jsonify, render_template,render_template_string,request, url_for, flash, redirect, session,Blueprint,g
from flask_user import roles_required, UserManager, UserMixin
from flask_login import LoginManager, login_required, logout_user, login_user, current_user
#from flask_ldap3_login import AuthenticationResponse,AuthenticationResponseStatus
#from flask_ldap3_login import LDAP3LoginManager
from werkzeug.exceptions import abort
#from flask_sqlalchemy import SQLAlchemy
#from app.dbmodels.user import User
from app.main import dashboard
from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO,Branches
from app.dbmodels.user import User,UserRoles,Role
from app.dbmodels.formc import Remittance,Remittance_Purpose
#dashboard = Blueprint('dashboard', __name__)
dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')




dt = datetime.datetime.now()

def parseElements(elements):
	all_elements = {}
	for name, element in elements:
		all_elements[name] = {}
		all_elements[name]['optional'] = element.is_optional
		if hasattr(element.type, 'elements'):
			all_elements[name]['type'] = parseElements(
				element.type.elements)
		else:
			all_elements[name]['type'] = str(element.type)

	return all_elements


def check_sql_string(sql, values):
	unique = "%PARAMETER%"
	sql = sql.replace("?", unique)
	for v in values: sql = sql.replace(unique, repr(v), 1)
	return sql



@dashboard.route('/list')
@login_required
def taxlist():
	try:
		
		'''user = User.query.filter_by(Username = current_user.Username ).first()
		print (user)
		print ('Role : ')
		print (current_user.has_roles('Checker'))

		print ('Branch...')
		print (current_user.Branch)'''
		
		print ('......dashboard_index123....')
		tin_list = []
		print (current_user)
		cust_branch = current_user.Branch.strip()
		print (cust_branch)
		if cust_branch == 'PO':
			cust_branch = 'PBBR'
		branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
		print ('branch')
		print (branch.Code)
		br_code = branch.Code
		if br_code == '4001':
			br_code = '4005'

		print (br_code)
		
		if current_user.has_roles('Admin'):
			tin_list = TININFO.query.filter_by(status=0).order_by(TININFO.id.desc()).all()
			#tin_list = TININFO.query.all()
			#tin_list = TININFO.query.filter_by(branch_code=br_code,status=0).all()
			#print (tin_list)
		else:
			tin_list = TININFO.query.filter_by(branch_code=br_code,status=0).order_by(TININFO.id.desc()).all()

		print ('tin list ')
		print (tin_list)

		return render_template('dashboard/list.html',tin_list=tin_list)
	except Exception as e:
		print(e)
		return render_template('dashboard/list.html',tin_list=tin_list)



@dashboard.route('/approvelist',methods = ['POST', 'GET'])
@login_required
def approvelist():
	
	tin_list = []
	print (current_user)
	cust_branch = current_user.Branch.strip()
	print (cust_branch)
	if cust_branch == 'PO':
		cust_branch = 'PBBR'
	
	branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
	print (branch.Code)
	br_code = branch.Code
	if br_code == '4001':
		br_code = '4005'

	print (br_code)
		
	if current_user.has_roles('Admin'):
		tin_list = TININFO.query.filter_by(status=1).order_by(TININFO.id.desc()).all()
		#tin_list = TININFO.query.filter_by(branch_code=br_code,status=0).all()
		#print (tin_list)
	else:
		tin_list = TININFO.query.filter_by(branch_code=br_code,status=1).order_by(TININFO.id.desc()).all()
	
	return render_template('dashboard/approvelist.html',tin_list= tin_list)


@dashboard.route('/rejectlist',methods = ['POST', 'GET'])
@login_required
def rejectlist():
	
	tin_list = []
	print (current_user)
	cust_branch = current_user.Branch.strip()
	print (cust_branch)
	if cust_branch == 'PO':
		cust_branch = 'PBBR'
	
	branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
	print (branch.Code)
	br_code = branch.Code
	if br_code == '4001':
		br_code = '4005'

	print (br_code)
		
	if current_user.has_roles('Admin'):
		tin_list = TININFO.query.filter_by(status=2).order_by(TININFO.id.desc()).all()
		#tin_list = TININFO.query.filter_by(branch_code=br_code,status=0).all()
		#print (tin_list)
	else:
		tin_list = TININFO.query.filter_by(branch_code=br_code,status=2).order_by(TININFO.id.desc()).all()
	
	return render_template('dashboard/rejectlist.html',tin_list= tin_list)


@dashboard.route('/approve/<string:id>',methods = ['POST', 'GET'])
@login_required
def approve(id):
	print (current_user)
	user = User.query.filter_by(Username = current_user.Username ).first()
	print (user)
	tin = TININFO.query.filter_by(id=id).first()
	print (tin)
	#cust_no = customerid
	now = datetime.datetime.now()
	print ("Current date and time : ")
	#print (now.strftime("%Y-%m-%d %H:%M:%S"))
	print (now.strftime("%d%m%Y"))

	if tin:
		response = app.utils.update_tin_cbs(id,tin.tin_no,tin.financial_year,tin.customer_basic)
		
		print (response)
		
		dt 						  = datetime.datetime.now()
		tin.status = 1
		tin.approve_by = user.id
		tin.updated_at = dt
		mobile = tin.mobile
		msg = 'Congratulations!! Succeffully Update Your Tax Return Copy. '
		db.session.commit()
		flash ('Updated Tax Retrun  information  Successfully','success')
		ssl_otp_response=app.utils.smsnewapi(mobile,msg)
		
	else:
		flash ('Unsuccessful!!!','success')
	return redirect('/dashboard/list')
	#return render_template_string('hello')

@dashboard.route('/reject/<string:id>',methods = ['POST', 'GET'])
@login_required
def reject(id):
	print (current_user)
	user = User.query.filter_by(Username = current_user.Username ).first()
	print (user)
	tin = TININFO.query.filter_by(id=id).first()
	print (tin)
	#cust_no = customerid
	now = datetime.datetime.now()
	print ("Current date and time : ")
	#print (now.strftime("%Y-%m-%d %H:%M:%S"))
	print (now.strftime("%d%m%Y"))
	

	if tin:
		#response = app.utils.update_tin_cbs(id,tin.tin_no,tin.financial_year,tin.customer_basic)
		
		#print (response)
		
		dt 						  = datetime.datetime.now()
		tin.status = 2
		tin.approve_by = user.id
		tin.updated_at = dt
		mobile = tin.mobile
		msg = 'Sorry!! Your submitted Tax Return Copy has been rejected. Please for any Query call 16207. '
		db.session.commit()
		flash (' Tax Retrun  information Rejected!!!','danger')
		ssl_otp_response=app.utils.smsnewapi(mobile,msg)
	else:
		flash ('Unsuccessful!!!','success')
	return redirect('/dashboard/list')











						   

@dashboard.route('/formclist')
@login_required
def formclist():
	try:
		formc_list = []
		cust_branch = current_user.Branch.strip()
		branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
		if current_user.has_roles('Admin'):
			#tin_list = TININFO.query.filter_by(status=0).all()
			#formc_list = Remittance.query.filter_by(status=0).all().order_by()
			formc_list = Remittance.query.order_by(Remittance.id.desc()).all()
			return render_template('dashboard/formclist.html',formc_list=formc_list)
	except Exception as e:	
		print(e)
		return render_template('dashboard/formclist.html',formc_list=formc_list)








@dashboard.route('/formc')
@login_required
def indexformc():
	try:
		#rejected_customer_list = riskgradingrequests.query.filter_by(status='rejected').filter_by(requestedby=current_user.Username).all()
		print ('test')
	except Exception as e:
		print(e)
	
	finally:
		return render_template('dashboard/formc.html')

@dashboard.route('/updateformc/<id>')
def updateformc(id):
	try:
		#self.print_date = print_date
		#self.print_status = print_status
		#self.printed_by = printed_by
		user = User.query.filter_by(Username = current_user.Username ).first()
		dt = datetime.datetime.now()
		#user               = User.query.filter_by(Username=username).first()
		formc_list = Remittance.query.filter_by(id=id).first()
		formc_list.print_status = 1 
		formc_list.print_date = dt
		formc_list.printed_by = user.id
		db.session.commit()
		data = {'status': 'success'}
		
		return jsonify(data)



	except Exception as e:
		print(e)
		data = {'status': 'failure'}
		return jsonify(data)



@dashboard.route('/viewemail/<id>')
@login_required
def viewemail(id):
	customer = []

	try:
		customer = CUSTINFO.query.filter_by(id=id).first()
		print (customer.external_account)
	except Exception as e:	
		print(e)
	finally:
		return render_template('dashboard/email_view.html',customer=customer)
	



@dashboard.route('/viewformc/<id>')
@login_required
def viewformc(id):
	try:
		formc_list = []
		purpose = ''
		print_date = ''
		dt = datetime.datetime.now()
		purposes = Remittance_Purpose.query.all()
		
		print ('date:....')
		print (dt)
		#cust_branch = current_user.Branch.strip()
		#branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
		#if current_user.has_roles('Admin'):
			#tin_list = TININFO.query.filter_by(status=0).all()
			#formc_list = Remittance.query.filter_by(status=0).all()
		formc_list = Remittance.query.filter_by(id=id).first()
		print ('formc list ')
		print (formc_list.application_date)
		print (formc_list.purpose_of_remittance_id)
		print_date 						  = dt.strftime("%d/%m/%Y")
		#print (print_date)
		
		if formc_list.purpose_of_remittance_id > 0:
			purpose_id = formc_list.purpose_of_remittance_id
			purpose_res = Remittance_Purpose.query.filter_by(id=purpose_id).first()
			purpose = purpose_res.name
		else:
			purpose = formc_list.ictPurposeSpecify
		#print (formc_list)
		
	except Exception as e:	
		print(e)
	finally:
		#return render_template('dashboard/formc.html')
		if formc_list.remittance_type == 'ICT':
			return render_template('dashboard/formcict.html',formc_list=formc_list,purpose=purpose,print_date=print_date,purposes =purposes )
		else:	
			return render_template('dashboard/formcdetails.html',formc_list=formc_list,purpose=purpose,print_date=print_date,purposes =purposes )


@dashboard.route('/')
@login_required
def index():
		
	if current_user.is_authenticated:
		print (current_user.Username)
		print ('***********dashboard*************')
		user = User.query.filter_by(Username=current_user.Username).first()
		role_name = user.user_role
		print ('***********Role : *************')
		print (role_name)
		return render_template('dashboard/index.html',role_name=role_name) 
	else:
		return render_template('accounts/login.html')


@dashboard.route('/email_list')
@login_required
def emaillist():
	try :
		email_list = []
		cust_branch = current_user.Branch.strip()
		print (cust_branch)
		if cust_branch == 'PO':
			cust_branch = 'PBBR'
		branch = Branches.query.filter_by(Mnemonic=cust_branch).first()
		print ('branch')
		print (branch.Code)
		br_code = branch.Code
		if br_code == '4001':
			br_code = '4005'
			print (br_code)
		
		if current_user.has_roles('Admin'):
			email_list = CUSTINFO.query.filter_by(status=1).order_by(CUSTINFO.id.desc()).all()
			#tin_list = TININFO.query.all()
			#tin_list = TININFO.query.filter_by(branch_code=br_code,status=0).all()
			#print (tin_list)
		else:
			email_list = CUSTINFO.query.filter_by(status = 1).order_by(CUSTINFO.id.desc()).all()

		print ('email_list list ')
		print (email_list)

		return render_template('dashboard/email_list.html',email_list=email_list)
	except Exception as e:
		print(e)
		return render_template('dashboard/email_list.html',email_list=email_list)
	
	
		







