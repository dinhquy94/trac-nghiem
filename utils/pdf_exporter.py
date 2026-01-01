from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
import random
import os

class PDFExporter:
    """Export exam to PDF"""
    
    def __init__(self):
        """Initialize PDF exporter with Vietnamese font support"""
        # Try multiple font sources
        self.font_name = 'Helvetica'
        self.font_name_bold = 'Helvetica-Bold'
        
        # 1. Try DejaVu Sans from fonts folder
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fonts')
        
        try:
            font_regular = os.path.join(font_path, 'DejaVuSans.ttf')
            font_bold = os.path.join(font_path, 'DejaVuSans-Bold.ttf')
            
            if os.path.exists(font_regular) and os.path.exists(font_bold):
                # Verify it's actually a TTF file
                with open(font_regular, 'rb') as f:
                    header = f.read(4)
                    if header in [b'\x00\x01\x00\x00', b'true', b'typ1']:
                        pdfmetrics.registerFont(TTFont('VietnameseFont', font_regular))
                        pdfmetrics.registerFont(TTFont('VietnameseFont-Bold', font_bold))
                        self.font_name = 'VietnameseFont'
                        self.font_name_bold = 'VietnameseFont-Bold'
                        print(f"✓ Loaded DejaVu Sans fonts from: {font_path}")
                        return
        except Exception as e:
            print(f"⚠ Could not load DejaVu fonts: {e}")
        
        # 2. Try system Arial (macOS)
        system_fonts = [
            '/Library/Fonts/Arial Unicode.ttf',
            '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
            '/Library/Fonts/Arial.ttf',
            '/System/Library/Fonts/Supplemental/Arial.ttf'
        ]
        
        for arial_font in system_fonts:
            if os.path.exists(arial_font):
                try:
                    pdfmetrics.registerFont(TTFont('VietnameseFont', arial_font))
                    self.font_name = 'VietnameseFont'
                    self.font_name_bold = 'VietnameseFont'
                    print(f"✓ Using system Arial font: {arial_font}")
                    return
                except Exception as e:
                    continue
        
        # 3. Fallback to Helvetica
        print(f"⚠ Using Helvetica (may not display Vietnamese correctly)")
        print(f"⚠ To fix: Download Vietnamese fonts manually to {font_path}")
    
    def export_exam(self, exam, questions, output_path, shuffle_questions=False, shuffle_answers=False, include_answers=False):
        """Export exam to PDF with beautiful formatting"""
        
        # Shuffle questions if requested
        if shuffle_questions:
            questions = random.sample(questions, len(questions))
        
        # Create PDF with margins
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4,
            rightMargin=2*cm, 
            leftMargin=2*cm,
            topMargin=2.5*cm, 
            bottomMargin=2*cm,
            title=exam['title']
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles with Vietnamese font support
        styles = getSampleStyleSheet()
        
        # Header style - School/Department
        header_style = ParagraphStyle(
            'Header',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            alignment=TA_CENTER,
            fontName=self.font_name_bold,
            spaceAfter=5
        )
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=10,
            spaceBefore=10,
            alignment=TA_CENTER,
            fontName=self.font_name_bold,
            leading=20
        )
        
        # Info box style
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495E'),
            alignment=TA_CENTER,
            fontName=self.font_name,
            spaceAfter=20
        )
        
        # Instruction style
        instruction_style = ParagraphStyle(
            'Instruction',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            alignment=TA_JUSTIFY,
            fontName=self.font_name,
            spaceAfter=15,
            leftIndent=10,
            rightIndent=10
        )
        
        # Question number style
        question_num_style = ParagraphStyle(
            'QuestionNum',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            fontName=self.font_name_bold,
            spaceAfter=5
        )
        
        # Question text style
        question_text_style = ParagraphStyle(
            'QuestionText',
            parent=styles['Normal'],
            fontSize=10.5,
            textColor=colors.HexColor('#2C3E50'),
            fontName=self.font_name,
            spaceAfter=8,
            leading=14
        )
        
        # Option style
        option_style = ParagraphStyle(
            'Option',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#34495E'),
            leftIndent=25,
            spaceAfter=4,
            fontName=self.font_name,
            leading=13
        )
        
        # Answer style (if showing answers)
        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#27ae60'),
            leftIndent=25,
            spaceAfter=5,
            fontName=self.font_name_bold,
            leading=12
        )
        
        # ===== DECORATIVE LINE =====
        # Decorative line at top
        line_table = Table([['']], colWidths=[doc.width])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#667eea')),
        ]))
        elements.append(line_table)
        
        elements.append(Spacer(1, 0.5*cm))
        
        # ===== TITLE =====
        exam_type = exam.get('exam_type', 'test')
        exam_type_text = 'ĐỀ ÔN TẬP' if exam_type == 'practice' else 'ĐỀ KIỂM TRA'
        title = Paragraph(f"<b>{exam_type_text}</b><br/>{exam['title']}", title_style)
        elements.append(title)
        
        # ===== INFO BOX =====
        info_data = []
        if exam.get('duration', 0) > 0:
            info_data.append([
                Paragraph(f"<b>Thời gian:</b> {exam['duration']} phút", info_style),
                Paragraph(f"<b>Số câu:</b> {len(questions)}", info_style),
                Paragraph(f"<b>Tổng điểm:</b> {exam.get('total_points', len(questions))}", info_style)
            ])
        else:
            info_data.append([
                Paragraph(f"<b>Số câu:</b> {len(questions)}", info_style),
                Paragraph(f"<b>Tổng điểm:</b> {exam.get('total_points', len(questions))}", info_style),
                Paragraph("<b>Không giới hạn thời gian</b>", info_style)
            ])
        
        info_table = Table(info_data, colWidths=[doc.width/3]*3)
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(info_table)
        
        elements.append(Spacer(1, 0.3*cm))
        
        # ===== INSTRUCTIONS =====
        if exam.get('description'):
            desc = Paragraph(f"<i>{exam['description']}</i>", instruction_style)
            elements.append(desc)
        
        instruction_text = "Học sinh không được sử dụng tài liệu. Giám thị không giải thích gì thêm."
        instruction = Paragraph(f"<i>{instruction_text}</i>", instruction_style)
        elements.append(instruction)
        
        elements.append(Spacer(1, 0.5*cm))
        
        elements.append(Spacer(1, 0.5*cm))
        
        # ===== QUESTIONS SECTION =====
        for idx, question in enumerate(questions, 1):
            # Keep question and its options together
            question_elements = []
            
            # Question number and points combined with question text on same line
            points_text = ""
            if question.get('points', 1) != 1:
                points_text = f" ({question['points']} điểm)"
            
            # Combine question number and text on same line
            q_combined = Paragraph(
                f"<b>Câu {idx}:{points_text}</b> {question['question_text']}", 
                question_text_style
            )
            question_elements.append(q_combined)
            
            # Options (for multiple choice)
            if question['question_type'] == 'multiple_choice':
                options = question['options'][:]
                
                # Shuffle answers if requested
                if shuffle_answers and not include_answers:
                    correct_answer = question['correct_answer']
                    # Find the correct option
                    correct_option = None
                    for opt in options:
                        if opt.startswith(correct_answer):
                            correct_option = opt
                            break
                    
                    # Shuffle
                    random.shuffle(options)
                
                for option in options:
                    # Highlight correct answer if showing answers
                    if include_answers and option.startswith(question['correct_answer']):
                        opt_para = Paragraph(f"<b>{option} ✓</b>", answer_style)
                    else:
                        opt_para = Paragraph(option, option_style)
                    question_elements.append(opt_para)
            
            elif question['question_type'] == 'true_false':
                opt_a = Paragraph("A. Đúng", option_style)
                opt_b = Paragraph("B. Sai", option_style)
                
                if include_answers:
                    if question['correct_answer'] == 'Đúng':
                        opt_a = Paragraph("<b>A. Đúng ✓</b>", answer_style)
                    else:
                        opt_b = Paragraph("<b>B. Sai ✓</b>", answer_style)
                
                question_elements.append(opt_a)
                question_elements.append(opt_b)
            
            # Add explanation if showing answers and explanation exists
            if include_answers and question.get('explanation'):
                expl_text = f"<i>Giải thích: {question['explanation']}</i>"
                expl_para = Paragraph(expl_text, answer_style)
                question_elements.append(expl_para)
            
            # Add spacing between questions
            question_elements.append(Spacer(1, 0.4*cm))
            
            # Keep question together on same page
            elements.append(KeepTogether(question_elements))
        
        # ===== FOOTER =====
        elements.append(Spacer(1, 1*cm))
        
        footer_data = [[
            Paragraph("<i>--- HẾT ---</i>", ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                fontName=self.font_name_bold
            ))
        ]]
        footer_table = Table(footer_data, colWidths=[doc.width])
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        return output_path
