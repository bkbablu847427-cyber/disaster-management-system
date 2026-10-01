# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='public')   # public, responder, admin
    phone = db.Column(db.String(15))
    organization = db.Column(db.String(200))
    location = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reported_incidents = db.relationship('Incident', foreign_keys='Incident.reported_by', backref='reporter', lazy=True)
    assigned_incidents = db.relationship('Incident', foreign_keys='Incident.assigned_to', backref='assignee', lazy=True)

class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    disaster_type = db.Column(db.String(50), default="General")
    severity = db.Column(db.String(20), default="Medium")  # Low, Medium, High, Critical
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Active')  # Active, In Progress, Resolved, Closed
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    priority = db.Column(db.String(20), default='Medium')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))  # Medical, Food, Shelter, Transport, etc
    quantity = db.Column(db.Integer)
    unit = db.Column(db.String(20))
    location = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)
    allocated_to = db.Column(db.Integer, db.ForeignKey('incident.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)