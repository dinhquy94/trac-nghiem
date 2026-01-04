from datetime import datetime
from bson.objectid import ObjectId

class Question:
    """Question model"""
    
    @staticmethod
    def create(db, exam_id, question_text, question_type, options, correct_answer, difficulty, points=1, explanation='', media_url='', support_content='', group_prompt=''):
        """Create a new question
        
        Args:
            media_url: URL for listening/speaking/reading/writing questions (audio/video)
            support_content: Supporting text/content for skill questions
            group_prompt: Prompt text for group questions (where multiple questions share one prompt)
        """
        question_data = {
            'exam_id': ObjectId(exam_id) if isinstance(exam_id, str) else exam_id,
            'question_text': question_text,
            'question_type': question_type,  # 'multiple_choice', 'true_false', 'essay', 'listening', 'speaking', 'reading', 'writing', 'group'
            'options': options,  # List of options for multiple choice
            'correct_answer': correct_answer,  # Correct answer(s)
            'difficulty': difficulty,  # 'easy', 'medium', 'hard'
            'points': points,
            'explanation': explanation,  # AI-generated explanation for learning
            'media_url': media_url,  # URL for media (listening/speaking/reading/writing)
            'support_content': support_content,  # Supporting content for skill questions
            'group_prompt': group_prompt,  # Shared prompt for group questions
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.questions.insert_one(question_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(db, question_id):
        """Find question by ID"""
        if isinstance(question_id, str):
            question_id = ObjectId(question_id)
        return db.questions.find_one({'_id': question_id})
    
    @staticmethod
    def find_by_exam(db, exam_id):
        """Find all questions for an exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        return list(db.questions.find({'exam_id': exam_id}).sort('created_at', 1))
    
    @staticmethod
    def update(db, question_id, update_data):
        """Update question"""
        if isinstance(question_id, str):
            question_id = ObjectId(question_id)
        update_data['updated_at'] = datetime.utcnow()
        return db.questions.update_one({'_id': question_id}, {'$set': update_data})
    
    @staticmethod
    def delete(db, question_id):
        """Delete question"""
        if isinstance(question_id, str):
            question_id = ObjectId(question_id)
        return db.questions.delete_one({'_id': question_id})
    
    @staticmethod
    def delete_by_exam(db, exam_id):
        """Delete all questions for an exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        return db.questions.delete_many({'exam_id': exam_id})
    
    @staticmethod
    def count_by_difficulty(db, exam_id):
        """Count questions by difficulty level"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        pipeline = [
            {'$match': {'exam_id': exam_id}},
            {'$group': {'_id': '$difficulty', 'count': {'$sum': 1}}}
        ]
        result = list(db.questions.aggregate(pipeline))
        return {item['_id']: item['count'] for item in result}
