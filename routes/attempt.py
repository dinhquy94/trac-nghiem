from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from routes.auth import login_required
from models.exam import Exam
from models.question import Question
from models.exam_attempt import ExamAttempt
from datetime import datetime

attempt_bp = Blueprint('attempt', __name__, url_prefix='/attempts')

@attempt_bp.route('/exam/<exam_id>/start', methods=['GET', 'POST'])
@login_required
def start_exam(exam_id):
    """Start taking an exam"""
    from app import db
    
    exam = Exam.find_by_id(db, exam_id)
    if not exam:
        flash('Không tìm thấy đề thi', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    # Check if exam is accessible
    if not exam['is_public'] and str(exam['owner_id']) != session['user_id']:
        flash('Bạn không có quyền làm đề thi này', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    if request.method == 'POST':
        # Create new attempt
        try:
            attempt_id = ExamAttempt.create(db, exam_id, session['user_id'])
            return redirect(url_for('attempt.take_exam', attempt_id=str(attempt_id)))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return redirect(url_for('main.student_dashboard'))
    
    # Show exam info and start button
    questions = Question.find_by_exam(db, exam_id)
    previous_attempts = ExamAttempt.find_by_exam_and_student(db, exam_id, session['user_id'])
    
    return render_template('attempt/start.html', 
                         exam=exam, 
                         question_count=len(questions),
                         previous_attempts=previous_attempts)

@attempt_bp.route('/<attempt_id>/take')
@login_required
def take_exam(attempt_id):
    """Take exam interface"""
    from app import db
    
    attempt = ExamAttempt.find_by_id(db, attempt_id)
    if not attempt:
        flash('Không tìm thấy bài thi', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    # Check permission
    if str(attempt['student_id']) != session['user_id']:
        flash('Bạn không có quyền xem bài thi này', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    # Check if already submitted
    if attempt['status'] == 'submitted' or attempt['status'] == 'graded':
        flash('Bài thi đã được nộp', 'warning')
        return redirect(url_for('attempt.view_result', attempt_id=attempt_id))
    
    exam = Exam.find_by_id(db, attempt['exam_id'])
    questions = Question.find_by_exam(db, attempt['exam_id'])
    
    return render_template('attempt/take.html', 
                         attempt=attempt, 
                         exam=exam, 
                         questions=questions)

@attempt_bp.route('/<attempt_id>/submit', methods=['POST'])
@login_required
def submit_exam(attempt_id):
    """Submit exam answers"""
    from app import db
    
    attempt = ExamAttempt.find_by_id(db, attempt_id)
    if not attempt:
        return jsonify({'success': False, 'message': 'Không tìm thấy bài thi'}), 404
    
    # Check permission
    if str(attempt['student_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    # Check if already submitted
    if attempt['status'] == 'submitted' or attempt['status'] == 'graded':
        return jsonify({'success': False, 'message': 'Bài thi đã được nộp'}), 400
    
    # Get answers from form
    answers = {}
    for key, value in request.form.items():
        if key.startswith('question_'):
            question_id = key.replace('question_', '')
            answers[question_id] = value
    
    try:
        # Submit attempt
        ExamAttempt.submit(db, attempt_id, answers)
        
        # Auto-grade multiple choice and true/false questions
        exam = Exam.find_by_id(db, attempt['exam_id'])
        questions = Question.find_by_exam(db, attempt['exam_id'])
        
        score = 0
        max_score = 0
        
        for question in questions:
            q_id = str(question['_id'])
            max_score += question.get('points', 1)
            
            # Only auto-grade multiple choice and true/false
            if question['question_type'] in ['multiple_choice', 'true_false']:
                student_answer = answers.get(q_id, '')
                correct_answer = question['correct_answer']
                
                # Normalize answers for comparison
                if student_answer.strip().upper() == correct_answer.strip().upper():
                    score += question.get('points', 1)
        
        # Grade attempt
        graded_attempt = ExamAttempt.grade(db, attempt_id, score, max_score, exam['passing_score'])
        
        # Award medals to student
        from models.user import User
        medals_earned = 1  # 1 medal for completing exam
        
        if graded_attempt and graded_attempt.get('passed'):
            medals_earned += 1  # Additional medal for passing
        
        if exam.get('exam_type') == 'practice':
            # Practice exams always give medals for participation
            User.add_medal(db, session['user_id'], medals_earned)
        else:
            # Test exams give medals based on result
            User.add_medal(db, session['user_id'], medals_earned)
        
        flash('Đã nộp bài thành công!', 'success')
        return jsonify({'success': True, 'redirect': url_for('attempt.view_result', attempt_id=attempt_id)})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Có lỗi xảy ra: {str(e)}'}), 500

@attempt_bp.route('/<attempt_id>/result')
@login_required
def view_result(attempt_id):
    """View exam result"""
    from app import db
    
    attempt = ExamAttempt.find_by_id(db, attempt_id)
    if not attempt:
        flash('Không tìm thấy bài thi', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    # Check permission
    exam = Exam.find_by_id(db, attempt['exam_id'])
    is_owner = str(exam['owner_id']) == session['user_id']
    is_student = str(attempt['student_id']) == session['user_id']
    
    if not is_owner and not is_student:
        flash('Bạn không có quyền xem kết quả này', 'danger')
        return redirect(url_for('main.student_dashboard'))
    
    questions = Question.find_by_exam(db, attempt['exam_id'])
    
    # Get user info if teacher viewing
    student = None
    if is_owner:
        from models.user import User
        student = User.find_by_id(db, attempt['student_id'])
    
    return render_template('attempt/result.html', 
                         attempt=attempt, 
                         exam=exam, 
                         questions=questions,
                         student=student)

@attempt_bp.route('/my-attempts')
@login_required
def my_attempts():
    """View all my exam attempts"""
    from app import db
    
    attempts = ExamAttempt.find_by_student(db, session['user_id'])
    
    # Get exam info for each attempt
    attempts_with_exams = []
    for attempt in attempts:
        exam = Exam.find_by_id(db, attempt['exam_id'])
        attempts_with_exams.append({
            'attempt': attempt,
            'exam': exam
        })
    
    return render_template('attempt/my_attempts.html', attempts=attempts_with_exams)
