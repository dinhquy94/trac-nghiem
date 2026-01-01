from datetime import datetime
from bson.objectid import ObjectId

class Document:
    """Document model for storing uploaded documents"""
    
    @staticmethod
    def create(db, title, content, file_path, file_type, owner_id, description=''):
        """Create a new document"""
        document_data = {
            'title': title,
            'description': description,
            'content': content,  # Extracted text content
            'file_path': file_path,
            'file_type': file_type,  # pdf, docx, txt, md
            'owner_id': ObjectId(owner_id) if isinstance(owner_id, str) else owner_id,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.documents.insert_one(document_data)
        return result.inserted_id
    
    @staticmethod
    def find_by_id(db, document_id):
        """Find document by ID"""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)
        return db.documents.find_one({'_id': document_id})
    
    @staticmethod
    def find_by_owner(db, owner_id, limit=None):
        """Find documents by owner"""
        if isinstance(owner_id, str):
            owner_id = ObjectId(owner_id)
        query = {'owner_id': owner_id}
        cursor = db.documents.find(query).sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def find_all(db, limit=None):
        """Find all documents"""
        cursor = db.documents.find().sort('created_at', -1)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    
    @staticmethod
    def update(db, document_id, update_data):
        """Update document"""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)
        update_data['updated_at'] = datetime.utcnow()
        return db.documents.update_one({'_id': document_id}, {'$set': update_data})
    
    @staticmethod
    def delete(db, document_id):
        """Delete document"""
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)
        return db.documents.delete_one({'_id': document_id})
    
    @staticmethod
    def search(db, query, owner_id=None):
        """Search documents by title or content"""
        search_query = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}}
            ]
        }
        if owner_id:
            if isinstance(owner_id, str):
                owner_id = ObjectId(owner_id)
            search_query['owner_id'] = owner_id
        return list(db.documents.find(search_query).sort('created_at', -1))
