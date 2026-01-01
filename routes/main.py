from flask import Blueprint, render_template, session
from routes.auth import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page"""
    if 'user_id' in session:
        if session.get('role') == 'teacher':
            # Redirect to teacher dashboard with data
            from flask import redirect, url_for
            return redirect(url_for('main.teacher_dashboard'))
        else:
            # Redirect to student dashboard with data
            from flask import redirect, url_for
            return redirect(url_for('main.student_dashboard'))
    return render_template('main/index.html')

@main_bp.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    """Teacher dashboard"""
    from app import db
    from models.exam import Exam
    from models.document import Document
    
    exams = Exam.find_by_owner(db, session['user_id'], limit=10)
    documents = Document.find_by_owner(db, session['user_id'], limit=10)
    
    return render_template('main/teacher_dashboard.html', 
                         exams=exams, 
                         documents=documents)

@main_bp.route('/student/dashboard')
@login_required
def student_dashboard():
    """Student dashboard"""
    from app import db
    from models.exam import Exam
    from models.exam_attempt import ExamAttempt
    from models.user import User
    
    public_exams = Exam.find_public(db, limit=20)
    my_attempts = ExamAttempt.find_by_student(db, session['user_id'], limit=10)
    top_students = User.get_top_students(db, limit=10)
    
    return render_template('main/student_dashboard.html', 
                         exams=public_exams,
                         attempts=my_attempts,
                         top_students=top_students)
