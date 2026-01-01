#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test PDF export with Vietnamese font"""

from utils.pdf_exporter import PDFExporter
from datetime import datetime

# Sample exam data
exam = {
    'title': 'Kiểm tra Toán học - Lớp 12',
    'description': 'Đề thi gồm 10 câu trắc nghiệm. Thí sinh không được sử dụng tài liệu.',
    'duration': 45,
    'total_points': 10,
    'passing_score': 50,
    'exam_type': 'test'
}

# Sample questions
questions = [
    {
        'question_text': 'Tập xác định của hàm số y = √(x - 2) là:',
        'question_type': 'multiple_choice',
        'options': [
            'A. [2; +∞)',
            'B. (-∞; 2]',
            'C. (2; +∞)',
            'D. (-∞; 2)'
        ],
        'correct_answer': 'A',
        'points': 1,
        'difficulty': 'easy',
        'explanation': 'Biểu thức dưới dấu căn phải không âm, tức là x - 2 ≥ 0 ⇔ x ≥ 2'
    },
    {
        'question_text': 'Đạo hàm của hàm số y = x³ - 3x² + 2x - 1 là:',
        'question_type': 'multiple_choice',
        'options': [
            'A. 3x² - 6x + 2',
            'B. 3x² - 6x + 1',
            'C. 3x² - 3x + 2',
            'D. x² - 6x + 2'
        ],
        'correct_answer': 'A',
        'points': 1,
        'difficulty': 'medium',
        'explanation': 'Áp dụng công thức đạo hàm: (x^n)\' = n.x^(n-1)'
    },
    {
        'question_text': 'Giới hạn lim(x→2) (x² - 4)/(x - 2) bằng:',
        'question_type': 'multiple_choice',
        'options': [
            'A. 4',
            'B. 2',
            'C. 0',
            'D. Không tồn tại'
        ],
        'correct_answer': 'A',
        'points': 1,
        'difficulty': 'medium',
        'explanation': 'Phân tích: (x² - 4)/(x - 2) = (x - 2)(x + 2)/(x - 2) = x + 2. Khi x → 2 thì giới hạn = 4'
    },
    {
        'question_text': 'Hàm số y = -x² + 4x - 3 đạt giá trị lớn nhất bằng:',
        'question_type': 'multiple_choice',
        'options': [
            'A. 1',
            'B. 2',
            'C. 3',
            'D. 4'
        ],
        'correct_answer': 'A',
        'points': 1,
        'difficulty': 'hard'
    },
    {
        'question_text': 'Nguyên hàm của hàm số f(x) = 2x + 1 là:',
        'question_type': 'multiple_choice',
        'options': [
            'A. x² + x + C',
            'B. x² + C',
            'C. 2x² + x + C',
            'D. x² + x'
        ],
        'correct_answer': 'A',
        'points': 1,
        'difficulty': 'easy',
        'explanation': '∫(2x + 1)dx = x² + x + C'
    },
    {
        'question_text': 'Phương trình x² - 5x + 6 = 0 có hai nghiệm là:',
        'question_type': 'true_false',
        'options': ['Đúng', 'Sai'],
        'correct_answer': 'Đúng',
        'points': 1,
        'difficulty': 'easy',
        'explanation': 'Δ = 25 - 24 = 1 > 0, nên phương trình có 2 nghiệm phân biệt'
    },
    {
        'question_text': 'Tích phân ∫₀¹ x dx = 1/2',
        'question_type': 'true_false',
        'options': ['Đúng', 'Sai'],
        'correct_answer': 'Đúng',
        'points': 1,
        'difficulty': 'medium',
        'explanation': '∫₀¹ x dx = [x²/2]₀¹ = 1/2 - 0 = 1/2'
    }
]

# Test PDF export
print("Testing PDF export with Vietnamese font...")
exporter = PDFExporter()

# Export without answers
print("\n1. Exporting exam without answers...")
output1 = '/Users/quynd/Projects/de_thi_ai/test_exam_no_answers.pdf'
exporter.export_exam(exam, questions, output1, shuffle_questions=False, shuffle_answers=False, include_answers=False)
print(f"✓ Exported to: {output1}")

# Export with answers
print("\n2. Exporting exam with answers and explanations...")
output2 = '/Users/quynd/Projects/de_thi_ai/test_exam_with_answers.pdf'
exporter.export_exam(exam, questions, output2, shuffle_questions=False, shuffle_answers=False, include_answers=True)
print(f"✓ Exported to: {output2}")

# Export with shuffled questions
print("\n3. Exporting exam with shuffled questions...")
output3 = '/Users/quynd/Projects/de_thi_ai/test_exam_shuffled.pdf'
exporter.export_exam(exam, questions, output3, shuffle_questions=True, shuffle_answers=True, include_answers=False)
print(f"✓ Exported to: {output3}")

print("\n✅ All tests completed! Please check the generated PDF files.")
print("   Font tiếng Việt should display correctly with DejaVu Sans.")
