#!/usr/bin/env python3
"""
Database initialization script for MyTube
"""
import os
import sys
import getpass
from app import create_app, db
from app.models import User, Category
from flask_migrate import upgrade

def init_database():
    """Initialize database with tables and admin user."""
    app = create_app()
    
    with app.app_context():
        print("Initializing MyTube database...")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            print(f"Admin user already exists: {admin_user.username}")
            return
        
        # Create admin user
        print("\nCreating system administrator account...")
        
        while True:
            username = input("Enter admin username: ").strip()
            if username and len(username) >= 3:
                # Check if username exists
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    break
                print("Username already exists. Please choose another.")
            else:
                print("Username must be at least 3 characters long.")
        
        while True:
            email = input("Enter admin email: ").strip()
            if email and '@' in email:
                # Check if email exists
                existing_user = User.query.filter_by(email=email).first()
                if not existing_user:
                    break
                print("Email already exists. Please choose another.")
            else:
                print("Please enter a valid email address.")
        
        while True:
            password = getpass.getpass("Enter admin password: ")
            if len(password) >= 6:
                confirm_password = getpass.getpass("Confirm admin password: ")
                if password == confirm_password:
                    break
                print("Passwords do not match. Please try again.")
            else:
                print("Password must be at least 6 characters long.")
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            password=password,
            role='admin'
        )
        
        db.session.add(admin_user)
        
        # Create default categories
        print("\nCreating default categories...")
        default_categories = [
            {
                'name': 'General',
                'description': 'General purpose videos',
                'is_shared': True
            },
            {
                'name': 'Education',
                'description': 'Educational content',
                'is_shared': True
            },
            {
                'name': 'Entertainment',
                'description': 'Entertainment videos',
                'is_shared': True
            },
            {
                'name': 'Technology',
                'description': 'Technology and programming content',
                'is_shared': True
            }
        ]
        
        for cat_data in default_categories:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                is_shared=cat_data['is_shared'],
                created_by=admin_user.id
            )
            db.session.add(category)
        
        # Commit changes
        db.session.commit()
        
        print(f"\n✅ Database initialized successfully!")
        print(f"Admin user created: {username}")
        print(f"Admin email: {email}")
        print("Default categories created.")
        print("\nYou can now start the application.")

if __name__ == '__main__':
    try:
        init_database()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error initializing database: {str(e)}")
        sys.exit(1)
