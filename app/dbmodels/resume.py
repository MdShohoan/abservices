from app import app,db
import ldap3
import json

class Resume(db.Model):
	__tablename__ = 'resumes'
	id              = db.Column(db.Integer, primary_key=True)
	full_name   = db.Column(db.String(255), nullable=True)
	experience   = db.Column(db.String(255), nullable=True)
	email   = db.Column(db.String(255), nullable=True)
	phone   = db.Column(db.String(15), nullable=False)
	gender   = db.Column(db.String(5), nullable=False)
	cv   = db.Column(db.String(100), nullable=False)
	interests   = db.Column(db.Text, nullable=False)
	objective   = db.Column(db.Text, nullable=False)
	created_at =  db.Column(db.DateTime, nullable=False)
	remarks   = db.Column(db.Text, nullable=False)
	status   = db.Column(db.Integer, nullable=False)
	#id = db.Column(db.Integer, primary_key=True)
	#filename = db.Column(db.String(50))

	def __init__(self,id,full_name,experience,email,phone,gender,cv,interests,objective,created_at,remarks,status):

		self.id = id
		self.full_name = full_name
		self.experience = experience
		self.email = email
		self.phone = phone
		self.gender = gender
		self.cv = cv
		self.interests = interests
		self.objective  = objective
		self.created_at = created_at
		self.remarks = remarks
		self.status = status
		
	def __repr__(self):
		return f"<Item {self.id}>"

	@property
	def serialize(self):
		"""
		Return item in serializeable format
		"""

		return { 

			"id" : self.id,
			"full_name" : self.full_name,
			"experience" : self.experience,
			"email" : self.email,
			"phone" : self.phone,
			"gender" : self.gender,
			"cv" : self.cv,
			"interests" : self.interests,
			"objective"    : self.objective,
			"created_at" : self.created_at,
			"remarks" : self.remarks,
			"status" : self.status
			
		}