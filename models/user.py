from datetime import datetime
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    """User model"""
    
    @staticmethod
    def create(db, username, email, password, role='student', full_name='', avatar_url=''):
        """Create a new user"""
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'role': role,  # 'teacher' or 'student'
            'full_name': full_name,
            'avatar_url': avatar_url or 'https://ui-avatars.com/api/?name=' + username + '&background=667eea&color=fff',
            'medals': 0,  # Số huy chương
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.users.insert_one(user_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(db, user_id):
        """Find user by ID"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db.users.find_one({'_id': user_id})
    
    @staticmethod
    def find_by_username(db, username):
        """Find user by username"""
        return db.users.find_one({'username': username})
    
    @staticmethod
    def find_by_email(db, email):
        """Find user by email"""
        return db.users.find_one({'email': email})
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """Verify password"""
        return check_password_hash(stored_password, provided_password)
    
    @staticmethod
    def update(db, user_id, update_data):
        """Update user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        update_data['updated_at'] = datetime.utcnow()
        return db.users.update_one({'_id': user_id}, {'$set': update_data})
    
    @staticmethod
    def update_profile(db, user_id, update_data):
        """Update user profile information"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        update_data['updated_at'] = datetime.utcnow()
        result = db.users.update_one({'_id': user_id}, {'$set': update_data})
        return result.modified_count > 0
    
    @staticmethod
    def change_password(db, user_id, new_password):
        """Change user password"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        hashed_password = generate_password_hash(new_password)
        result = db.users.update_one(
            {'_id': user_id},
            {'$set': {
                'password': hashed_password,
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def add_medal(db, user_id, count=1):
        """Add medal to user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db.users.update_one(
            {'_id': user_id},
            {
                '$inc': {'medals': count},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
    
    @staticmethod
    def get_top_students(db, limit=10):
        """Get top students by medals"""
        return list(db.users.find(
            {'role': 'student'},
            {'password': 0}
        ).sort('medals', -1).limit(limit))
    
    @staticmethod
    def get_all_students(db):
        """Get all students"""
        return list(db.users.find(
            {'role': 'student'},
            {'password': 0}
        ).sort('username', 1))
