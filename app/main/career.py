import os
import smtplib
import datetime
import requests
import random
import uuid
from flask import render_template, send_file,send_from_directory
from flask import Blueprint,Markup, current_app,render_template, url_for, request,session, redirect,jsonify,flash,abort
from flask_wtf.csrf import CSRFProtect,generate_csrf
from flask_wtf.csrf import CSRFError
#from app.models import CUSTINFO, OTPModel,SMSINFO,OTP_HISTORY,CBS_CUSTOMERS,TININFO,REMITCUSTINFO
from werkzeug.utils import secure_filename
import logging
import logging.config
from sqlalchemy.orm.session import Session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from smtplib import SMTPException


#from logging.handlers import TimedRotatingFileHandler
from app.main import formc
import app.utils
from app import db 
from app import LOG
from app.dbmodels.resume import Resume
career = Blueprint('career', __name__, url_prefix='/career')
#current_app.config["BASE_URL"]

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
	os.mkdir(UPLOAD_FOLDER)

current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set([ 'pdf'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_template(filename,email):
	
	if (filename):
		with open(filename, "rb") as f:
			charset = 'utf-8'
			text = f.read().decode(charset).replace('{email}',email)
		
		return text

def send_email_resume (receiver_email,sender_email,email_subject,name,email) :

	#sender = 'noreply@abbl.com'
	#print (email)
	#email = ['saidur@abbl.com']
	#sender = 'donotreply@abbl.com'
	#email = ['najmul@abbl.com', 'tkhanum@abbl.com','saidur@abbl.com']
	#receivers = ['najmul@abbl.com', 'tkhanum@abbl.com','saidur@abbl.com']
	#receivers = ['saidur@abbl.com']
	#receivers = [email]
	#receivers = email
	sender = sender_email
	receivers = receiver_email
	subject = email_subject
	#subject = "ABBL Internet Banking - On-Demand Tokencode" + alert_type
	#print ("subject:")
	#print (subject)
	current_file = os.path.abspath(os.path.dirname(__file__))
	email_filename = os.path.join(current_file, '../../email_template_resume.txt')
	#email_filename = os.path.join(current_file, 'email_template_resume.txt')
	print (email_filename)
	
	try:
		
		msg = MIMEMultipart() 
		# storing the senders email address 
		msg['From'] = sender 
		# storing the receivers email address 
		#msg['To'] =  ", ".join(receivers)  
		msg['To'] = receivers
		# storing the subject 
		#msg['Subject'] = "Test Email with attachment"
		msg['Subject'] = subject
		#body = read_template('email_template.txt',message)
		body = read_template(email_filename,email)
		#print (body)
		msg.attach(MIMEText(body, 'plain'))
		text = msg.as_string() 
		smtpObj = smtplib.SMTP('mail.abbl.com', 25)
		#smtpObj = smtplib.SMTP('localhost')
		if (email):
			res = smtpObj.sendmail(sender, receivers, text)
			#update_sending_status(mydb,cursor,id)    
			#print (res)
			#print ("Successfully sent email")
			#flash('An email has been sent ','alert alert-success')
	except SMTPException as e:
		print (e)
		print ("Error: unable to send email")


# Create index function for upload and return files
@career.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		error = 1
		dt = datetime.datetime.now()
		# check if the post request has the file part
		if 'file' not in request.files:
			flash('No file part','alert alert-warning')
			return redirect(request.url)
		file = request.files['file']
		if file.filename == '':
			flash('No file selected for uploading','alert alert-warning')
			return redirect(request.url)
		if file and allowed_file(file.filename):
			
			id 						  = dt.strftime("%Y%m%d%H%M%S%f")
			filename =  id+secure_filename(file.filename)
			cv_filename = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
			
			file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
			#flash('File successfully uploaded')
			error = 0
			#return redirect('/')
		else:
			flash('Allowed file type is pdf only.','alert alert-warning')
			return redirect(request.url)
		
		if not error : 
			file = request.files['file']
			full_name = request.form['fullname']
			experience = request.form['experience']
			email = request.form['email']
			phone = request.form['phone']
			gender = request.form['gender']
			cv = filename
			#interests = request.form ['interests']
			interests_list = request.form.getlist('interests')
			interests=  ", ".join(interests_list)
			#interests ='it'
			objective = request.form['objective']
			#objective = 'cv'
			created_at = dt

			#remarks = request.form['']
			remarks = ''
			status = 1
			id 						  = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
			resume = Resume(id,full_name,experience,email,phone,gender,cv,interests,objective,created_at,remarks,status)
			try:

				db.session.add(resume)
				db.session.commit()
				
				receiver_email = 'saidur@abbl.com'
				sender_email = 'donotreply@abbl.com'
				email_subject = 'ABBL Resume Management - A new CV has been Uploaded'
				name = full_name
				send_email_resume (receiver_email,sender_email,email_subject,name,email)
				flash('Congratulations !! Successfully Uploaded Your Resume','alert alert-success')
			except Exception as e:
				flash(str(e),'alert alert-warning')
				print (e)
				return redirect(request.url)
		
			#upload = Upload(filename=file.filename, data=file.read())
			#db.session.add(upload)
			#db.session.commit()
			#return f'Uploaded: {cv.filename}'
	return render_template('career/index.html')

# create download function for download files
'''@career.route('/download/<upload_id>')
def download(upload_id):
	upload = Resume.query.filter_by(id=upload_id).first()
	return send_file(BytesIO(upload.data), download_name=upload.filename, as_attachment=True)
'''
@career.route('/download/<path:filename>', methods=['GET', 'POST'])
def download(filename):
	current_file = os.path.abspath(os.path.dirname(__file__))
	#uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
	uploads = os.path.join(current_file, current_app.config['UPLOAD_FOLDER'])
	#return send_from_directory(uploads, filename)
	return send_file(filename, download_name=filename, as_attachment=True)	
