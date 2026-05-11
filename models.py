from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(255), nullable=False) # hashed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to predictions
    predictions = db.relationship('Prediction', backref='patient', lazy=True)

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    disease_type = db.Column(db.String(50), nullable=False) # Heart / Kidney / Liver
    risk_result = db.Column(db.String(50), nullable=False) # High / Low
    probability = db.Column(db.Float, nullable=True) # e.g. 75.50
    city = db.Column(db.String(50), nullable=True) # Location
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
