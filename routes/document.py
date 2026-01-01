from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.utils import secure_filename
from routes.auth import login_required, teacher_required
from models.document import Document
from utils.file_handler import allowed_file, extract_text_from_file, save_uploaded_file
import os

document_bp = Blueprint('document', __name__, url_prefix='/documents')

@document_bp.route('/')
@login_required
@teacher_required
def list_documents():
    """List all documents"""
    from app import db
    documents = Document.find_by_owner(db, session['user_id'])
    return render_template('document/list.html', documents=documents)

@document_bp.route('/create', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_document():
    """Create a new document"""
    if request.method == 'POST':
        from app import db
        
        title = request.form.get('title')
        description = request.form.get('description', '')
        content_type = request.form.get('content_type')  # 'file' or 'markdown'
        
        if not title:
            flash('Vui lòng nhập tiêu đề tài liệu', 'danger')
            return render_template('document/create.html')
        
        content = ''
        file_path = ''
        file_type = ''
        
        if content_type == 'file':
            # Handle file upload
            if 'file' not in request.files:
                flash('Vui lòng chọn file để tải lên', 'danger')
                return render_template('document/create.html')
            
            file = request.files['file']
            if file.filename == '':
                flash('Vui lòng chọn file để tải lên', 'danger')
                return render_template('document/create.html')
            
            if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
                # Save file
                file_path = save_uploaded_file(file, current_app.config['UPLOAD_FOLDER'])
                file_type = file.filename.rsplit('.', 1)[1].lower()
                
                # Extract text
                content = extract_text_from_file(file_path, file_type)
                
                if not content:
                    flash('Không thể trích xuất nội dung từ file', 'warning')
            else:
                flash('Định dạng file không được hỗ trợ. Vui lòng chọn file PDF, DOCX, TXT hoặc MD', 'danger')
                return render_template('document/create.html')
        
        elif content_type == 'markdown':
            # Handle markdown input
            content = request.form.get('markdown_content', '')
            file_type = 'md'
            
            if not content:
                flash('Vui lòng nhập nội dung tài liệu', 'danger')
                return render_template('document/create.html')
        
        # Create document
        try:
            Document.create(db, title, content, file_path, file_type, session['user_id'], description)
            flash('Tạo tài liệu thành công!', 'success')
            return redirect(url_for('document.list_documents'))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('document/create.html')
    
    return render_template('document/create.html')

@document_bp.route('/<document_id>')
@login_required
def view_document(document_id):
    """View document details"""
    from app import db
    document = Document.find_by_id(db, document_id)
    
    if not document:
        flash('Không tìm thấy tài liệu', 'danger')
        return redirect(url_for('document.list_documents'))
    
    # Check permission
    if str(document['owner_id']) != session['user_id'] and session.get('role') != 'teacher':
        flash('Bạn không có quyền xem tài liệu này', 'danger')
        return redirect(url_for('document.list_documents'))
    
    return render_template('document/view.html', document=document)

@document_bp.route('/<document_id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_document(document_id):
    """Edit document"""
    from app import db
    document = Document.find_by_id(db, document_id)
    
    if not document:
        flash('Không tìm thấy tài liệu', 'danger')
        return redirect(url_for('document.list_documents'))
    
    # Check permission
    if str(document['owner_id']) != session['user_id']:
        flash('Bạn không có quyền chỉnh sửa tài liệu này', 'danger')
        return redirect(url_for('document.list_documents'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description', '')
        content = request.form.get('content', '')
        
        if not title:
            flash('Vui lòng nhập tiêu đề tài liệu', 'danger')
            return render_template('document/edit.html', document=document)
        
        # Update document
        update_data = {
            'title': title,
            'description': description,
            'content': content
        }
        
        try:
            Document.update(db, document_id, update_data)
            flash('Cập nhật tài liệu thành công!', 'success')
            return redirect(url_for('document.view_document', document_id=document_id))
        except Exception as e:
            flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
            return render_template('document/edit.html', document=document)
    
    return render_template('document/edit.html', document=document)

@document_bp.route('/<document_id>/delete', methods=['POST'])
@login_required
@teacher_required
def delete_document(document_id):
    """Delete document"""
    from app import db
    document = Document.find_by_id(db, document_id)
    
    if not document:
        flash('Không tìm thấy tài liệu', 'danger')
        return redirect(url_for('document.list_documents'))
    
    # Check permission
    if str(document['owner_id']) != session['user_id']:
        flash('Bạn không có quyền xóa tài liệu này', 'danger')
        return redirect(url_for('document.list_documents'))
    
    try:
        # Delete file if exists
        if document.get('file_path') and os.path.exists(document['file_path']):
            os.remove(document['file_path'])
        
        Document.delete(db, document_id)
        flash('Xóa tài liệu thành công!', 'success')
    except Exception as e:
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
    
    return redirect(url_for('document.list_documents'))
