from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class voters(db.Model):
    full_name = db.Column(db.String(100))
    phone = db.Column(db.String(15), primary_key=True)
    dob = db.Column(db.String(10))
    gender = db.Column(db.String(10))
    religion = db.Column(db.String(50))
    has_voted = db.Column(db.Boolean, default=False)

class Candidate(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    party = db.Column(db.String(100))
    vote_count = db.Column(db.Integer, default=0)
