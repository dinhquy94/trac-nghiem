from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash
from models.user import User
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def teacher_required(f):
    """Decorator to require teacher role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục', 'warning')
            return redirect(url_for('auth.login'))
        if session.get('role') != 'teacher':
            flash('Bạn không có quyền truy cập trang này', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        from app import db
        
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role', 'student')
        
        # Validation
        if not all([full_name, username, email, password, confirm_password]):
            flash('Vui lòng điền đầy đủ thông tin', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự', 'danger')
            return render_template('auth/register.html')
        
        # Check if user exists
        if User.find_by_username(db, username):
            flash('Tên đăng nhập đã tồn tại', 'danger')
            return render_template('auth/register.html')
        
        if User.find_by_email(db, email):
            flash('Email đã được sử dụng', 'danger')
            return render_template('auth/register.html')
        
        # Create user
        try:
            User.create(db, username, email, password, role, full_name)
            flash('Đăng ký thành công! Vui lòng đăng nhập', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        from app import db
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not all([username, password]):
            flash('Vui lòng điền đầy đủ thông tin', 'danger')
            return render_template('auth/login.html')
        
        # Find user
        user = User.find_by_username(db, username)
        
        if user and User.verify_password(user['password'], password):
            # Set session
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']
            session.permanent = True
            
            flash(f'Chào mừng {user["username"]}!', 'success')
            
            # Redirect based on role
            if user['role'] == 'teacher':
                return redirect(url_for('main.teacher_dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng', 'danger')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Đã đăng xuất thành công', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile"""
    from app import db
    user = User.find_by_id(db, session['user_id'])
    return render_template('auth/profile.html', user=user)

@auth_bp.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    from app import db
    from werkzeug.utils import secure_filename
    import os
    from datetime import datetime
    
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    
    if not all([full_name, email]):
        flash('Vui lòng điền đầy đủ thông tin', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Check if email is taken by another user
    existing_user = User.find_by_email(db, email)
    if existing_user and str(existing_user['_id']) != session['user_id']:
        flash('Email đã được sử dụng bởi tài khoản khác', 'danger')
        return redirect(url_for('auth.profile'))
    
    update_data = {
        'full_name': full_name,
        'email': email
    }
    
    # Handle avatar upload or URL
    avatar_url = None
    if 'avatar_file' in request.files:
        file = request.files['avatar_file']
        if file and file.filename != '':
            # Check file extension
            ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
            if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                # Check file size (5MB max)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > 5 * 1024 * 1024:
                    flash('Kích thước ảnh không được vượt quá 5MB!', 'danger')
                    return redirect(url_for('auth.profile'))
                
                # Generate unique filename
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                name, ext = os.path.splitext(filename)
                unique_filename = f"avatar_{session['user_id']}_{timestamp}{ext}"
                
                # Save file
                upload_folder = current_app.config['UPLOAD_FOLDER']
                avatars_folder = os.path.join(upload_folder, 'avatars')
                os.makedirs(avatars_folder, exist_ok=True)
                
                filepath = os.path.join(avatars_folder, unique_filename)
                file.save(filepath)
                
                # Set avatar URL (relative path for serving)
                avatar_url = f'/uploads/avatars/{unique_filename}'
            else:
                flash('Định dạng file không hợp lệ! Hỗ trợ: JPG, PNG, GIF, WEBP', 'danger')
                return redirect(url_for('auth.profile'))
        elif not file or file.filename == '':
            # If no file uploaded, check for URL input
            avatar_url = request.form.get('avatar_url', '').strip()
    else:
        avatar_url = request.form.get('avatar_url', '').strip()
    
    # Update avatar if provided
    if avatar_url:
        update_data['avatar_url'] = avatar_url
    
    try:
        User.update_profile(db, session['user_id'], update_data)
        flash('Cập nhật thông tin thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change password"""
    from app import db
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not all([current_password, new_password, confirm_password]):
        flash('Vui lòng điền đầy đủ thông tin', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('Mật khẩu mới không khớp', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('Mật khẩu mới phải có ít nhất 6 ký tự', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Verify current password
    user = User.find_by_id(db, session['user_id'])
    if not User.verify_password(user['password'], current_password):
        flash('Mật khẩu hiện tại không đúng', 'danger')
        return redirect(url_for('auth.profile'))
    
    # Update password
    from werkzeug.security import generate_password_hash
    try:
        User.update(db, session['user_id'], {
            'password': generate_password_hash(new_password)
        })
        flash('Đổi mật khẩu thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))
