#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Initialize database with sample data for deployment
Run this after first deployment: docker-compose exec web python init_db.py
"""

from app import create_app
from models.user import User
from models.document import Document
from models.exam import Exam
import os

def init_database():
    """Initialize database with sample data"""
    app = create_app('production')
    
    with app.app_context():
        db = app.db
        
        print("=" * 60)
        print("INITIALIZING DATABASE")
        print("=" * 60)
        
        # 1. Check if admin user exists
        print("\n1. Checking admin user...")
        admin = User.find_by_username(db, 'admin')
        if admin:
            print("   ✓ Admin user already exists")
        else:
            print("   Creating admin user...")
            admin_id = User.create(
                db, 
                username='admin',
                password='admin@123',  # ⚠️ CHANGE THIS IN PRODUCTION
                email='admin@example.com',
                role='teacher',
                full_name='Quản trị viên'
            )
            print(f"   ✓ Admin user created: {admin_id}")
            print("   ⚠️  Default password: admin@123")
            print("   ⚠️  CHANGE THIS IMMEDIATELY!")
        
        # 2. Check if sample student exists
        print("\n2. Checking sample student...")
        student = User.find_by_username(db, 'student1')
        if student:
            print("   ✓ Sample student already exists")
        else:
            print("   Creating sample student...")
            student_id = User.create(
                db,
                username='student1',
                password='student@123',
                email='student@example.com',
                role='student',
                full_name='Học sinh Mẫu'
            )
            print(f"   ✓ Sample student created: {student_id}")
        
        # 3. Check collections exist
        print("\n3. Checking database collections...")
        collections = db.list_collection_names()
        required_collections = ['users', 'documents', 'exams', 'attempts']
        
        for collection in required_collections:
            if collection in collections:
                count = db[collection].count_documents({})
                print(f"   ✓ {collection}: {count} documents")
            else:
                print(f"   ⚠️  {collection}: empty (will be created on first use)")
        
        # 4. Create indexes
        print("\n4. Creating database indexes...")
        try:
            db.users.create_index('username', unique=True)
            print("   ✓ users.username index created")
        except:
            print("   ℹ users.username index already exists")
        
        try:
            db.users.create_index('email', unique=True)
            print("   ✓ users.email index created")
        except:
            print("   ℹ users.email index already exists")
        
        try:
            db.exams.create_index('created_by')
            print("   ✓ exams.created_by index created")
        except:
            print("   ℹ exams.created_by index already exists")
        
        try:
            db.attempts.create_index('exam_id')
            print("   ✓ attempts.exam_id index created")
        except:
            print("   ℹ attempts.exam_id index already exists")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        print("\nDefault credentials:")
        print("  Admin:")
        print("    Username: admin")
        print("    Password: admin@123 (CHANGE THIS!)")
        print("\n  Student:")
        print("    Username: student1")
        print("    Password: student@123")
        print("\n" + "=" * 60)

if __name__ == '__main__':
    init_database()
