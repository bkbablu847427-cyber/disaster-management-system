#!/usr/bin/env python
"""Initialize database with correct schema"""

from app import app, db
from models import User, Incident, Resource, ActivityLog
from werkzeug.security import generate_password_hash

# Create database tables
with app.app_context():
    db.create_all()
    
    # Create default admin user
    admin_exists = User.query.filter_by(username='admin').first()
    if not admin_exists:
        admin = User(
            username='admin',
            email='admin@example.com',
            password=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Database created with new schema")
        print("✓ Default admin user created")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("✓ Database recreated with new schema")
