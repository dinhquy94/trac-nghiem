import google.generativeai as genai
import json

class GeminiAI:
    """Gemini AI service for generating exam questions"""
    
    def __init__(self, api_key):
        """Initialize Gemini AI"""
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-3-flash-preview')
        else:
            self.model = None
    
    def generate_questions(self, document_content, num_questions=10, difficulty='medium', question_type='multiple_choice'):
        """Generate questions from document content"""
        if not self.model:
            raise Exception("Gemini API key not configured")
        
        difficulty_instructions = {
            'easy': 'Tạo câu hỏi dễ, phù hợp với học sinh có kiến thức cơ bản',
            'medium': 'Tạo câu hỏi trung bình, yêu cầu hiểu và áp dụng kiến thức',
            'hard': 'Tạo câu hỏi khó, yêu cầu phân tích và tổng hợp kiến thức'
        }
        
        question_type_instructions = {
            'multiple_choice': 'Câu hỏi trắc nghiệm với 4 đáp án A, B, C, D',
            'true_false': 'Câu hỏi đúng/sai',
            'essay': 'Câu hỏi tự luận ngắn'
        }
        
        prompt = f"""
Bạn là một giáo viên THPT chuyên nghiệp. Hãy tạo {num_questions} câu hỏi từ tài liệu sau:

{document_content[:4000]}  # Giới hạn nội dung để tránh vượt quá token limit

Yêu cầu:
- Loại câu hỏi: {question_type_instructions.get(question_type, 'Trắc nghiệm')}
- Mức độ: {difficulty_instructions.get(difficulty, 'Trung bình')}
- Câu hỏi phải liên quan trực tiếp đến nội dung tài liệu
- Đáp án phải chính xác và rõ ràng
- Phù hợp với học sinh THPT

Trả về kết quả dưới dạng JSON với format sau:
{{
  "questions": [
    {{
      "question_text": "Nội dung câu hỏi",
      "question_type": "{question_type}",
      "options": ["A. Đáp án 1", "B. Đáp án 2", "C. Đáp án 3", "D. Đáp án 4"],
      "correct_answer": "A",
      "difficulty": "{difficulty}",
      "explanation": "Giải thích ngắn gọn"
    }}
  ]
}}

CHÚ Ý: Chỉ trả về JSON, không thêm text nào khác.
"""
        
        try:
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            elif result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result_text = result_text.strip()
            
            # Parse JSON
            result = json.loads(result_text)
            return result.get('questions', [])
        
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response.text}")
            # Return empty list if parsing fails
            return []
        except Exception as e:
            print(f"Error generating questions: {e}")
            return []
    
    def generate_mixed_difficulty_questions(self, document_content, easy=3, medium=5, hard=2):
        """Generate questions with mixed difficulty levels"""
        questions = []
        
        if easy > 0:
            easy_questions = self.generate_questions(document_content, easy, 'easy')
            questions.extend(easy_questions)
        
        if medium > 0:
            medium_questions = self.generate_questions(document_content, medium, 'medium')
            questions.extend(medium_questions)
        
        if hard > 0:
            hard_questions = self.generate_questions(document_content, hard, 'hard')
            questions.extend(hard_questions)
        
        return questions
    
    def generate_explanation(self, question_text, correct_answer, question_context=''):
        """Generate explanation for a question answer"""
        if not self.model:
            raise Exception("Gemini API key not configured")
        
        prompt = f"""
Bạn là một giáo viên THPT nhiệt tình. Hãy giải thích tại sao đáp án này là đúng cho câu hỏi sau:

Câu hỏi: {question_text}

Đáp án đúng: {correct_answer}

{f"Bối cảnh: {question_context}" if question_context else ""}

Yêu cầu:
- Giải thích ngắn gọn, dễ hiểu (2-3 câu)
- Phù hợp với học sinh THPT
- Tập trung vào kiến thức cốt lõi
- Giúp học sinh hiểu sâu hơn về chủ đề

Chỉ trả về phần giải thích, không thêm text nào khác.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return ""
    
    def enhance_question_with_explanation(self, question_data, document_content=''):
        """Add AI-generated explanation to a question"""
        try:
            explanation = self.generate_explanation(
                question_data.get('question_text', ''),
                question_data.get('correct_answer', ''),
                document_content[:1000]  # Limit context
            )
            question_data['explanation'] = explanation
            return question_data
        except Exception as e:
            print(f"Error enhancing question: {e}")
            return question_data
