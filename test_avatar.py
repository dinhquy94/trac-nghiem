#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test avatar default functionality"""

from app import create_app
import os

app = create_app(os.getenv('FLASK_ENV', 'development'))

with app.app_context():
    from models.user import User
    from app import db
    
    print("Testing avatar default functionality...")
    print()
    
    # Test 1: User with no avatar
    print("1. Testing user with empty avatar_url:")
    test_user = {
        'username': 'testuser',
        'avatar_url': ''
    }
    
    from jinja2 import Template
    template = Template("{{ avatar_url|default_avatar(username) }}")
    
    with app.test_request_context():
        result = template.render(avatar_url='', username='testuser')
        print(f"   Empty avatar_url → {result}")
        assert 'ui-avatars.com' in result, "Should return default avatar"
        print("   ✓ Passed")
    
    # Test 2: User with valid avatar
    print("\n2. Testing user with valid avatar_url:")
    with app.test_request_context():
        result = template.render(avatar_url='https://example.com/avatar.jpg', username='testuser')
        print(f"   Valid URL → {result}")
        assert result == 'https://example.com/avatar.jpg', "Should return original URL"
        print("   ✓ Passed")
    
    # Test 3: User with None avatar
    print("\n3. Testing user with None avatar_url:")
    with app.test_request_context():
        result = template.render(avatar_url=None, username='johndoe')
        print(f"   None avatar_url → {result}")
        assert 'ui-avatars.com' in result, "Should return default avatar"
        assert 'johndoe' in result, "Should include username in URL"
        print("   ✓ Passed")
    
    # Test 4: Check actual user in database
    print("\n4. Checking users in database:")
    users = list(db.users.find().limit(3))
    for user in users:
        username = user.get('username')
        avatar = user.get('avatar_url', '')
        print(f"   @{username}: {avatar[:50]}{'...' if len(avatar) > 50 else ''}")
    
    print("\n✅ All avatar tests passed!")
    print("Avatar URLs will automatically show default if empty or None")

if __name__ == '__main__':
    print("Run this with: python test_avatar.py")
