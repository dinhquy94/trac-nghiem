from datetime import datetime
from bson.objectid import ObjectId

class Exam:
    """Exam model"""
    
    @staticmethod
    def create(db, title, description, owner_id, duration=60, passing_score=50, is_public=False, exam_type='test'):
        """Create a new exam"""
        exam_data = {
            'title': title,
            'description': description,
            'owner_id': ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
            'duration': duration,  # in minutes
            'passing_score': passing_score,  # percentage
            'is_public': is_public,
            'exam_type': exam_type,  # 'test' or 'practice'
            'total_points': 0,
            'question_count': 0,
            'difficulty_distribution': {
                'easy': 0,
                'medium': 0,
                'hard': 0
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.exams.insert_one(exam_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(db, exam_id):
        """Find exam by ID"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        return db.exams.find_one({'_id': exam_id})
    
    @staticmethod
    def find_by_owner(db, owner_id, limit=None):
        """Find exams by owner"""
        if isinstance(owner_id, str):
            owner_id = ObjectId(owner_id)
        cursor = db.exams.find({'owner_id': owner_id}).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_public(db, limit=None):
        """Find public exams"""
        cursor = db.exams.find({'is_public': True}).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_all(db, limit=None):
        """Find all exams"""
        cursor = db.exams.find().sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def update(db, exam_id, update_data):
        """Update exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        update_data['updated_at'] = datetime.utcnow()
        return db.exams.update_one({'_id': exam_id}, {'$set': update_data})
    
    @staticmethod
    def update_statistics(db, exam_id):
        """Update exam statistics (question count, total points, difficulty distribution)"""
        from models.question import Question
        
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        
        questions = Question.find_by_exam(db, exam_id)
        total_points = sum(q.get('points', 1) for q in questions)
        question_count = len(questions)
        
        difficulty_dist = Question.count_by_difficulty(db, exam_id)
        
        return Exam.update(db, exam_id, {
            'total_points': total_points,
            'question_count': question_count,
            'difficulty_distribution': {
                'easy': difficulty_dist.get('easy', 0),
                'medium': difficulty_dist.get('medium', 0),
                'hard': difficulty_dist.get('hard', 0)
            }
        })
    
    @staticmethod
    def delete(db, exam_id):
        """Delete exam"""
        if isinstance(exam_id, str):
            exam_id = ObjectId(exam_id)
        return db.exams.delete_one({'_id': exam_id})
    
    @staticmethod
    def search(db, query, owner_id=None):
        """Search exams by title or description"""
        search_query = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}}
            ]
        }
        if owner_id:
            if isinstance(owner_id, str):
                owner_id = ObjectId(owner_id)
            search_query['owner_id'] = owner_id
        return list(db.exams.find(search_query).sort('created_at', -1))
