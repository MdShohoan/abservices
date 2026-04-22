from app import app,db
import ldap3
import json


class Remittance_Purpose(db.Model):

	__tablename__ = 'remittance_purpose'
	__table_args__ = {'schema': 'abbl'}

	id              = db.Column(db.Integer, primary_key=True)
	name 			= db.Column(db.Text,nullable=False)

	def __init__(self,id,name):

		self.id = id
		self.name = name
	
	def __repr__(self):
		return f"<Item {self.id}>"

	
	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""

		return { 

			"id" : self.id,
			"name" : self.name
		}




class Remittance(db.Model):

	__tablename__ = 'remittance'
	__table_args__ = {'schema': 'abbl'}

	# IDs are generated as YYYYMMDDHHMMSSms-style integers (too large for 32-bit)
	id              = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
	remitter_name   = db.Column(db.String(255), nullable=False)
	remitter_address = db.Column(db.Text,nullable=False)
	remittance_amount = db.Column(db.Float,nullable=False)
	remittance_currency = db.Column(db.String(4), nullable=False)
	remitted_bank_name = db.Column(db.String(255), nullable=False)
	remitted_bank_address = db.Column(db.Text, nullable=False)
	purpose_of_remittance_id  = db.Column(db.Integer,nullable=False)
	applicant_name = db.Column(db.String(255), nullable=False)
	applicant_nationality = db.Column(db.String(50), nullable=False)
	applicant_address = db.Column(db.Text, nullable=False)
	application_date = db.Column(db.DateTime, nullable=False)
	print_date =  db.Column(db.DateTime, nullable=True)
	print_status = db.Column(db.Integer,nullable=False)
	printed_by = db.Column(db.Integer,nullable=True)
	remittance_type = db.Column(db.String(10),nullable=True)
	ictPurposeSpecify = db.Column(db.Text, nullable=False)
	applicant_mobile = db.Column(db.String(50),nullable=True)
	remittance_amount_words = db.Column(db.Text, nullable=True)
	remittance_reference  = db.Column(db.Text, nullable=True)

	def __init__(self,id,remitter_name,remitter_address,remittance_amount,remittance_currency,remitted_bank_name,remitted_bank_address,purpose_of_remittance_id,applicant_name,applicant_nationality,applicant_address,application_date,print_date,print_status,printed_by,remittance_type,ictPurposeSpecify,applicant_mobile,remittance_amount_words,remittance_reference):

		self.id = id
		self.remitter_name = remitter_name
		self.remitter_address = remitter_address
		self.remittance_amount = remittance_amount
		self.remittance_currency = remittance_currency
		self.remitted_bank_name = remitted_bank_name
		self.remitted_bank_address = remitted_bank_address
		self.purpose_of_remittance_id = purpose_of_remittance_id
		self.applicant_name  = applicant_name
		self.applicant_nationality = applicant_nationality
		self.applicant_address = applicant_address
		self.application_date = application_date
		self.print_date = print_date
		self.print_status = print_status
		self.printed_by = printed_by
		self.remittance_type = remittance_type
		self.ictPurposeSpecify = ictPurposeSpecify
		self.applicant_mobile = applicant_mobile
		self.remittance_amount_words = remittance_amount_words
		self.remittance_reference = remittance_reference
	
	def __repr__(self):
		return f"<Item {self.id}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""

		return { 

			"id" : self.id,
			"remitter_name" : self.remitter_name,
			"remitter_address" : self.remitter_address,
			"remittance_amount" : self.remittance_amount,
			"remittance_currency" : self.remittance_currency,
			"remitted_bank_name" : self.remitted_bank_name,
			"remitted_bank_address" : self.remitted_bank_address,
			"purpose_of_remittance_id" : self.purpose_of_remittance_id,
			"applicant_name"    : self.applicant_name,
			"applicant_nationality" : self.remitter_address,
			"applicant_address" : self.applicant_address,
			"application_date" : self.application_date,
			"print_date" : self.print_date,
			"print_status" : self.print_status,
			"printed_by" : self.printed_by,
			"remittance_type" :self.remittance_type,
			"ictPurposeSpecify" : self.ictPurposeSpecify,
			"applicant_mobile" : self.applicant_mobile,
			"remittance_amount_words" : self.remittance_amount_words,
			"remittance_reference" : self.remittance_reference
		}