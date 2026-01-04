from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file, current_app
from routes.auth import login_required, teacher_required
from models.exam import Exam
from models.question import Question
from models.document import Document
from models.exam_attempt import ExamAttempt
from utils.gemini_service import GeminiAI
from utils.pdf_exporter import PDFExporter
from utils.file_handler import save_media_file
from bson.objectid import ObjectId
import os
from datetime import datetime

exam_bp = Blueprint('exam', __name__, url_prefix='/exams')

@exam_bp.route('/')
@login_required
def list_exams():
    """List exams based on user role"""
    from app import db
    
    if session.get('role') == 'teacher':
        exams = Exam.find_by_owner(db, session['user_id'])
    else:
        exams = Exam.find_public(db)
    
    return render_template('exam/list.html', exams=exams)

@exam_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_exam():
    """Create a new exam"""
    if request.method == 'POST':
        from app import db
        
        title = request.form.get('title')
        description = request.form.get('description', '')
        duration = int(request.form.get('duration', 60))
        passing_score = int(request.form.get('passing_score', 50))
        is_public = request.form.get('is_public') == 'on'
        exam_type = request.form.get('exam_type', 'test')
        
        if not title:
            flash('Vui lòng nhập tiêu đề đề thi', 'danger')
            return render_template('exam/create.html')
        
        try:
            exam_id = Exam.create(db, title, description, session['user_id'], 
                                duration, passing_score, is_public, exam_type)
            flash('Tạo đề thi thành công!', 'success')
            return redirect(url_for('exam.edit_exam', exam_id=str(exam_id)))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('exam/create.html')
    
    return render_template('exam/create.html')

@exam_bp.route('/<exam_id>')
@login_required
def view_exam(exam_id):
    """View exam details"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam:
        flash('Không tìm thấy đề thi', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    # Check permission
    if not exam['is_public'] and str(exam['owner_id']) != session['user_id']:
        flash('Bạn không có quyền xem đề thi này', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    questions = Question.find_by_exam(db, exam_id)
    
    # Get statistics if teacher
    statistics = None
    attempts_with_students = []
    if session.get('role') == 'teacher' and str(exam['owner_id']) == session['user_id']:
        from models.user import User
        statistics = ExamAttempt.get_statistics(db, exam_id)
        attempts = ExamAttempt.find_by_exam(db, exam_id, limit=20)
        
        # Add student info to attempts
        for attempt in attempts:
            student = User.find_by_id(db, attempt['student_id'])
            username = student.get('username', 'N/A')
            avatar_url = student.get('avatar_url', '')
            
            # Ensure avatar has a default value
            if not avatar_url or avatar_url.strip() == '':
                avatar_url = f'https://ui-avatars.com/api/?name={username}&background=667eea&color=fff&size=128'
            
            attempt_data = dict(attempt)
            attempt_data['student_info'] = {
                'username': username,
                'full_name': student.get('full_name', ''),
                'avatar_url': avatar_url
            }
            attempts_with_students.append(attempt_data)
    
    return render_template('exam/view.html', 
                         exam=exam, 
                         questions=questions,
                         statistics=statistics,
                         attempts=attempts_with_students)

@exam_bp.route('/<exam_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_exam(exam_id):
    """Edit exam"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam:
        flash('Không tìm thấy đề thi', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    # Check permission
    if str(exam['owner_id']) != session['user_id']:
        flash('Bạn không có quyền chỉnh sửa đề thi này', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        duration = int(request.form.get('duration', 60))
        passing_score = int(request.form.get('passing_score', 50))
        is_public = request.form.get('is_public') == 'on'
        exam_type = request.form.get('exam_type', 'test')
        
        if not title:
            flash('Vui lòng nhập tiêu đề đề thi', 'danger')
            return render_template('exam/edit.html', exam=exam)
        
        update_data = {
            'title': title,
            'description': description,
            'duration': duration,
            'passing_score': passing_score,
            'is_public': is_public,
            'exam_type': exam_type
        }
        
        try:
            Exam.update(db, exam_id, update_data)
            flash('Cập nhật đề thi thành công!', 'success')
            return redirect(url_for('exam.view_exam', exam_id=exam_id))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    questions = Question.find_by_exam(db, exam_id)
    documents = Document.find_by_owner(db, session['user_id'])
    
    return render_template('exam/edit.html', exam=exam, questions=questions, documents=documents)

@exam_bp.route('/<exam_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_exam(exam_id):
    """Delete exam"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam:
        flash('Không tìm thấy đề thi', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    # Check permission
    if str(exam['owner_id']) != session['user_id']:
        flash('Bạn không có quyền xóa đề thi này', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    try:
        # Delete all questions
        Question.delete_by_exam(db, exam_id)
        # Delete exam
        Exam.delete(db, exam_id)
        flash('Xóa đề thi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('exam.list_exams'))

@exam_bp.route('/<exam_id>/questions/add', methods=['POST'])
@login_required
@teacher_required
def add_question(exam_id):
    """Add question to exam"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam or str(exam['owner_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    difficulty = request.form.get('difficulty')
    points = int(request.form.get('points', 1))
    
    # Initialize optional fields
    media_url = ''
    support_content = ''
    group_prompt = ''
    options = []
    correct_answer = ''
    
    # Get upload folder
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Get options based on question type
    if question_type == 'multiple_choice':
        options = [
            request.form.get('option_a'),
            request.form.get('option_b'),
            request.form.get('option_c'),
            request.form.get('option_d')
        ]
        correct_answer = request.form.get('correct_answer')
    elif question_type == 'true_false':
        options = ['Đúng', 'Sai']
        correct_answer = request.form.get('correct_answer')
    elif question_type in ['listening', 'speaking', 'reading', 'writing']:
        # Skill-based questions - handle both URL and file upload
        if 'media_file' in request.files and request.files['media_file'].filename:
            # Upload media file
            _, media_url = save_media_file(request.files['media_file'], upload_folder)
            if not media_url:
                flash('Định dạng media không được hỗ trợ. Hỗ trợ: mp3, wav, m4a, mp4, webm, avi, mov', 'danger')
                return redirect(url_for('exam.edit_exam', exam_id=exam_id))
        else:
            # Use media URL if provided
            media_url = request.form.get('media_url', '')
        
        support_content = request.form.get('support_content', '')
        correct_answer = request.form.get('correct_answer', '')
    elif question_type == 'group':
        # Group questions with shared prompt - can also have media
        group_prompt = request.form.get('group_prompt', '')
        
        # Handle media file for group questions
        if 'media_file' in request.files and request.files['media_file'].filename:
            _, media_url = save_media_file(request.files['media_file'], upload_folder)
            if not media_url:
                flash('Định dạng media không được hỗ trợ. Hỗ trợ: mp3, wav, m4a, mp4, webm, avi, mov', 'danger')
                return redirect(url_for('exam.edit_exam', exam_id=exam_id))
        else:
            media_url = request.form.get('media_url', '')
        
        correct_answer = request.form.get('correct_answer', '')
    else:  # essay
        options = []
        correct_answer = request.form.get('sample_answer', '')
    
    try:
        Question.create(db, exam_id, question_text, question_type, 
                       options, correct_answer, difficulty, points, 
                       media_url=media_url, support_content=support_content, 
                       group_prompt=group_prompt)
        Exam.update_statistics(db, exam_id)
        flash('Thêm câu hỏi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('exam.edit_exam', exam_id=exam_id))

@exam_bp.route('/<exam_id>/questions/<question_id>/edit', methods=['POST'])
@login_required
@teacher_required
def edit_question(exam_id, question_id):
    """Edit question"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam or str(exam['owner_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    question_text = request.form.get('question_text')
    question_type = request.form.get('question_type')
    difficulty = request.form.get('difficulty')
    points = int(request.form.get('points', 1))
    explanation = request.form.get('explanation', '')
    
    # Initialize optional fields
    media_url = ''
    support_content = ''
    group_prompt = ''
    options = []
    correct_answer = ''
    
    # Get upload folder
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    
    # Get options based on question type
    if question_type == 'multiple_choice':
        options = [
            f"A. {request.form.get('option_a')}",
            f"B. {request.form.get('option_b')}",
            f"C. {request.form.get('option_c')}",
            f"D. {request.form.get('option_d')}"
        ]
        correct_answer = request.form.get('correct_answer')
    elif question_type == 'true_false':
        options = ['Đúng', 'Sai']
        correct_answer = request.form.get('correct_answer')
    elif question_type in ['listening', 'speaking', 'reading', 'writing']:
        # Skill-based questions - handle both URL and file upload
        if 'media_file' in request.files and request.files['media_file'].filename:
            # Upload new media file
            _, media_url = save_media_file(request.files['media_file'], upload_folder)
            if not media_url:
                flash('Định dạng media không được hỗ trợ. Hỗ trợ: mp3, wav, m4a, mp4, webm, avi, mov', 'danger')
                return redirect(url_for('exam.edit_exam', exam_id=exam_id))
        else:
            # Use media URL if provided or keep existing
            media_url = request.form.get('media_url', '')
        
        support_content = request.form.get('support_content', '')
        correct_answer = request.form.get('correct_answer', '')
    elif question_type == 'group':
        # Group questions with shared prompt - can also have media
        group_prompt = request.form.get('group_prompt', '')
        
        # Handle media file for group questions
        if 'media_file' in request.files and request.files['media_file'].filename:
            _, media_url = save_media_file(request.files['media_file'], upload_folder)
            if not media_url:
                flash('Định dạng media không được hỗ trợ. Hỗ trợ: mp3, wav, m4a, mp4, webm, avi, mov', 'danger')
                return redirect(url_for('exam.edit_exam', exam_id=exam_id))
        else:
            media_url = request.form.get('media_url', '')
        
        correct_answer = request.form.get('correct_answer', '')
    else:  # essay
        options = []
        correct_answer = request.form.get('sample_answer', '')
    
    update_data = {
        'question_text': question_text,
        'question_type': question_type,
        'options': options,
        'correct_answer': correct_answer,
        'difficulty': difficulty,
        'points': points,
        'explanation': explanation,
        'media_url': media_url,
        'support_content': support_content,
        'group_prompt': group_prompt
    }
    
    try:
        Question.update(db, question_id, update_data)
        Exam.update_statistics(db, exam_id)
        flash('Cập nhật câu hỏi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('exam.edit_exam', exam_id=exam_id))

@exam_bp.route('/<exam_id>/questions/<question_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_question(exam_id, question_id):
    """Delete question"""
    from app import db
    exam = Exam.find_by_id(db, exam_id)
    
    if not exam or str(exam['owner_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    try:
        Question.delete(db, question_id)
        Exam.update_statistics(db, exam_id)
        flash('Xóa câu hỏi thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('exam.edit_exam', exam_id=exam_id))

@exam_bp.route('/<exam_id>/questions/<question_id>/generate-explanation', methods=['POST'])
@login_required
@teacher_required
def generate_question_explanation(exam_id, question_id):
    """Generate AI explanation for a question"""
    from app import db
    
    exam = Exam.find_by_id(db, exam_id)
    if not exam or str(exam['owner_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    question = Question.find_by_id(db, question_id)
    if not question:
        return jsonify({'success': False, 'message': 'Không tìm thấy câu hỏi'}), 404
    
    try:
        gemini = GeminiAI(current_app.config['GEMINI_API_KEY'])
        explanation = gemini.generate_explanation(
            question['question_text'],
            question['correct_answer']
        )
        
        Question.update(db, question_id, {'explanation': explanation})
        return jsonify({'success': True, 'explanation': explanation})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@exam_bp.route('/<exam_id>/generate-questions', methods=['POST'])
@login_required
@teacher_required
def generate_questions(exam_id):
    """Generate questions using AI"""
    from app import db
    
    exam = Exam.find_by_id(db, exam_id)
    if not exam or str(exam['owner_id']) != session['user_id']:
        return jsonify({'success': False, 'message': 'Không có quyền thực hiện'}), 403
    
    document_ids = request.form.getlist('document_ids')
    num_easy = int(request.form.get('num_easy', 3))
    num_medium = int(request.form.get('num_medium', 5))
    num_hard = int(request.form.get('num_hard', 2))
    
    if not document_ids:
        flash('Vui lòng chọn ít nhất một tài liệu', 'danger')
        return redirect(url_for('exam.edit_exam', exam_id=exam_id))
    
    # Get documents content
    documents_content = []
    for doc_id in document_ids:
        doc = Document.find_by_id(db, doc_id)
        if doc:
            documents_content.append(doc.get('content', ''))
    
    combined_content = '\n\n'.join(documents_content)
    
    if not combined_content:
        flash('Không thể lấy nội dung từ tài liệu', 'danger')
        return redirect(url_for('exam.edit_exam', exam_id=exam_id))
    
    # Generate questions using Gemini
    try:
        gemini = GeminiAI(current_app.config['GEMINI_API_KEY'])
        questions = gemini.generate_mixed_difficulty_questions(
            combined_content, 
            easy=num_easy, 
            medium=num_medium, 
            hard=num_hard
        )
        
        # Add questions to exam
        for q in questions:
            Question.create(
                db,
                exam_id,
                q.get('question_text', ''),
                q.get('question_type', 'multiple_choice'),
                q.get('options', []),
                q.get('correct_answer', ''),
                q.get('difficulty', 'medium'),
                1
            )
        
        Exam.update_statistics(db, exam_id)
        flash(f'Đã tạo {len(questions)} câu hỏi bằng AI!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra khi tạo câu hỏi: {str(e)}', 'danger')
    
    return redirect(url_for('exam.edit_exam', exam_id=exam_id))

@exam_bp.route('/<exam_id>/export-pdf')
@login_required
@teacher_required
def export_pdf(exam_id):
    """Export exam to PDF"""
    from app import db
    
    exam = Exam.find_by_id(db, exam_id)
    if not exam or str(exam['owner_id']) != session['user_id']:
        flash('Không có quyền thực hiện', 'danger')
        return redirect(url_for('exam.list_exams'))
    
    questions = Question.find_by_exam(db, exam_id)
    
    if not questions:
        flash('Đề thi chưa có câu hỏi', 'warning')
        return redirect(url_for('exam.view_exam', exam_id=exam_id))
    
    # Get options
    shuffle_questions = request.args.get('shuffle_questions') == '1'
    shuffle_answers = request.args.get('shuffle_answers') == '1'
    include_answers = request.args.get('include_answers') == '1'
    
    # Generate PDF
    try:
        output_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exports')
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"exam_{exam_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        exporter = PDFExporter()
        exporter.export_exam(exam, questions, output_path, 
                           shuffle_questions, shuffle_answers, include_answers)
        
        return send_file(output_path, as_attachment=True, download_name=f"{exam['title']}.pdf")
    except Exception as e:
        flash(f'Có lỗi xảy ra khi xuất PDF: {str(e)}', 'danger')
        return redirect(url_for('exam.view_exam', exam_id=exam_id))
