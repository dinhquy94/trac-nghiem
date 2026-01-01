from flask import Flask, current_app
from pymongo import MongoClient
from config import config
import os

# Proxy class to access db from current_app
class DBProxy:
    def __getattr__(self, name):
        try:
            return getattr(current_app.db, name)
        except (AttributeError, RuntimeError):
            raise RuntimeError("Working outside of application context or database not initialized.")

db = DBProxy()

def create_app(config_name='default'):
    """Create Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize MongoDB and attach to app
    mongo_client = MongoClient(app.config['MONGO_URI'])
    app.db = mongo_client.get_database()
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.document import document_bp
    from routes.exam import exam_bp
    from routes.attempt import attempt_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(exam_bp)
    app.register_blueprint(attempt_bp)
    
    # Route to serve uploaded files
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        """Serve uploaded files"""
        from flask import send_from_directory
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # Custom template filters
    @app.template_filter('datetime')
    def format_datetime(value, format='%d/%m/%Y %H:%M'):
        """Format datetime"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('date')
    def format_date(value, format='%d/%m/%Y'):
        """Format date"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.template_filter('string')
    def to_string(value):
        """Convert value to string (useful for ObjectId)"""
        return str(value)
    
    @app.template_filter('default_avatar')
    def default_avatar(avatar_url, username='User'):
        """Return default avatar if URL is empty or None"""
        if not avatar_url or avatar_url.strip() == '':
            # Generate avatar with user's initials using UI Avatars service
            return f'https://ui-avatars.com/api/?name={username}&background=667eea&color=fff&size=128'
        return avatar_url
    
    @app.context_processor
    def inject_user():
        """Inject current user info into all templates"""
        from flask import session
        if 'user_id' in session:
            from models.user import User
            user = User.find_by_id(current_app.db, session['user_id'])
            if user:
                avatar_url = user.get('avatar_url', '')
                if not avatar_url or avatar_url.strip() == '':
                    avatar_url = f'https://ui-avatars.com/api/?name={user.get("username", "User")}&background=667eea&color=fff&size=128'
                
                return dict(
                    current_user=user,
                    user_medals=user.get('medals', 0),
                    user_full_name=user.get('full_name', user.get('username')),
                    user_avatar=avatar_url
                )
        return dict(current_user=None, user_medals=0, user_full_name='', user_avatar='')
    
    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    if os.getenv('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        app.run(host='0.0.0.0', port=8080, debug=True)
