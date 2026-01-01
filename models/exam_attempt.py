from datetime import datetime
from bson.objectid import ObjectId

class ExamAttempt:
    """Exam attempt model for tracking student exam submissions"""
    
    @staticmethod
    def create(db, exam_id, student_id, answers=None):
        """Create a new exam attempt"""
        attempt_data = {
            'exam_id': ObjectId(exam_id) if isinstance(exam_id, str) else exam_id,
            'student_id': ObjectId(student_id) if isinstance(student_id, str) else student_id,
            'answers': answers or {},  # {question_id: answer}
            'score': 0,
            'max_score': 0,
            'percentage': 0,
            'passed': False,
            'status': 'in_progress',  # 'in_progress', 'submitted', 'graded'
            'started_at': datetime.utcnow(),
            'submitted_at': None,
            'graded_at': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.exam_attempts.insert_one(attempt_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(db, attempt_id):
        """Find attempt by ID"""
        if isinstance(attempt_id, str):
            attempt_id = ObjectId(attempt_id)
        return db.exam_attempts.find_one({'_id': attempt_id})
    
    @staticmethod
    def find_by_student(db, student_id, limit=None):
        """Find all attempts by a student"""
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        cursor = db.exam_attempts.find({'student_id': student_id}).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_by_exam(db, exam_id, limit=None):
        """Find all attempts for an exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        cursor = db.exam_attempts.find({'exam_id': exam_id}).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_by_exam_and_student(db, exam_id, student_id):
        """Find attempts for a specific exam by a specific student"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        if isinstance(student_id, str):
            student_id = ObjectId(student_id)
        return list(db.exam_attempts.find({
            'exam_id': exam_id,
            'student_id': student_id
        }).sort('created_at', -1))
    
    @staticmethod
    def update(db, attempt_id, update_data):
        """Update exam attempt"""
        if isinstance(attempt_id, str):
            attempt_id = ObjectId(attempt_id)
        update_data['updated_at'] = datetime.utcnow()
        return db.exam_attempts.update_one({'_id': attempt_id}, {'$set': update_data})
    
    @staticmethod
    def submit(db, attempt_id, answers):
        """Submit exam attempt"""
        update_data = {
            'answers': answers,
            'status': 'submitted',
            'submitted_at': datetime.utcnow()
        }
        return ExamAttempt.update(db, attempt_id, update_data)
    
    @staticmethod
    def grade(db, attempt_id, score, max_score, passing_score):
        """Grade exam attempt"""
        percentage = (score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= passing_score
        
        update_data = {
            'score': score,
            'max_score': max_score,
            'percentage': round(percentage, 2),
            'passed': passed,
            'status': 'graded',
            'graded_at': datetime.utcnow()
        }
        return ExamAttempt.update(db, attempt_id, update_data)
    
    @staticmethod
    def delete(db, attempt_id):
        """Delete exam attempt"""
        if isinstance(attempt_id, str):
            attempt_id = ObjectId(attempt_id)
        return db.exam_attempts.delete_one({'_id': attempt_id})
    
    @staticmethod
    def get_statistics(db, exam_id):
        """Get statistics for an exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        
        pipeline = [
            {'$match': {'exam_id': exam_id, 'status': 'graded'}},
            {'$group': {
                '_id': None,
                'total_attempts': {'$sum': 1},
                'avg_score': {'$avg': '$percentage'},
                'max_score': {'$max': '$percentage'},
                'min_score': {'$min': '$percentage'},
                'passed_count': {
                    '$sum': {'$cond': [{'$eq': ['$passed', True]}, 1, 0]}
                }
            }}
        ]
        
        result = list(db.exam_attempts.aggregate(pipeline))
        if result:
            stats = result[0]
            stats['pass_rate'] = (stats['passed_count'] / stats['total_attempts'] * 100) if stats['total_attempts'] > 0 else 0
            return stats
        return {
            'total_attempts': 0,
            'avg_score': 0,
            'max_score': 0,
            'min_score': 0,
            'passed_count': 0,
            'pass_rate': 0
        }
