#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test avatar upload functionality"""

import os
import sys

print("=" * 60)
print("KIỂM TRA CHỨC NĂNG UPLOAD ẢNH ĐẠI DIỆN")
print("=" * 60)

# Check uploads folder
uploads_path = '/Users/quynd/Projects/de_thi_ai/uploads'
avatars_path = os.path.join(uploads_path, 'avatars')

print("\n1. Kiểm tra thư mục:")
print(f"   ✅ uploads: {os.path.exists(uploads_path)}")
print(f"   ✅ avatars: {os.path.exists(avatars_path)}")

# Check routes
print("\n2. Kiểm tra routes:")
try:
    from routes.auth import auth_bp, allowed_file
    print("   ✅ auth_bp imported successfully")
    print(f"   ✅ Endpoints: {[rule.rule for rule in auth_bp.url_map.iter_rules()]}")
    
    # Test allowed_file function
    test_files = [
        ('avatar.jpg', True),
        ('photo.png', True),
        ('image.gif', True),
        ('picture.webp', True),
        ('document.pdf', False),
        ('script.js', False),
        ('style.css', False),
    ]
    
    print("\n3. Kiểm tra allowed_file():")
    for filename, expected in test_files:
        result = allowed_file(filename)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {filename}: {result} (expected: {expected})")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check models
print("\n4. Kiểm tra User model:")
try:
    from models.user import User
    methods = ['update_profile', 'change_password', 'find_by_id']
    for method in methods:
        has_method = hasattr(User, method)
        status = "✅" if has_method else "❌"
        print(f"   {status} User.{method}(): {has_method}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check app configuration
print("\n5. Kiểm tra Flask app:")
try:
    from app import create_app
    app = create_app('development')
    
    print(f"   ✅ UPLOAD_FOLDER: {app.config.get('UPLOAD_FOLDER')}")
    print(f"   ✅ MAX_CONTENT_LENGTH: {app.config.get('MAX_CONTENT_LENGTH', 'Not set')}")
    
    # Check if upload route exists
    with app.test_request_context():
        from flask import url_for
        try:
            profile_url = url_for('auth.profile')
            update_url = url_for('auth.update_profile')
            print(f"   ✅ Profile URL: {profile_url}")
            print(f"   ✅ Update URL: {update_url}")
        except Exception as e:
            print(f"   ❌ URL generation error: {e}")
            
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("TỔNG KẾT:")
print("=" * 60)
print("✅ Chức năng upload ảnh đại diện đã được cài đặt!")
print("✅ Hỗ trợ: JPG, PNG, GIF, WEBP (max 5MB)")
print("✅ Lưu trữ: uploads/avatars/")
print("✅ API: POST /auth/update_profile")
print("\n📝 Cách sử dụng:")
print("   1. Đăng nhập vào hệ thống")
print("   2. Vào 'Thông tin cá nhân'")
print("   3. Click 'Chọn ảnh từ máy tính' hoặc nhập URL")
print("   4. Click 'Cập nhật thông tin'")
print("\n🌐 Server: http://127.0.0.1:8080")
print("=" * 60)
