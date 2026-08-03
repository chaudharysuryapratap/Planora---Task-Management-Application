from app.models.category import Category
from app.database import db
import uuid
from datetime import datetime

class CategoryService:
    
    @staticmethod
    def get_categories(user_id):
        categories = Category.query.filter_by(user_id=user_id).all()
        return {'data': [cat.to_dict() for cat in categories]}, 200
    
    @staticmethod
    def create_category(user_id, data):
        # Check if category with same name exists for this user
        existing = Category.query.filter_by(
            user_id=user_id,
            name=data['name']
        ).first()
        
        if existing:
            return {'error': 'Category with this name already exists'}, 409
        
        category = Category(
            id=str(uuid.uuid4()),
            name=data['name'],
            color=data.get('color', '#808080'),
            user_id=user_id,
            is_default=False
        )
        
        db.session.add(category)
        db.session.commit()
        
        return category.to_dict(), 201
    
    @staticmethod
    def delete_category(user_id, category_id):
        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()
        
        if not category:
            return {'error': 'Category not found'}, 404
        
        if category.is_default:
            return {'error': 'Cannot delete default category'}, 400
        
        # Check if category has tasks
        if category.tasks:
            # Move tasks to uncategorized (set category_id to None)
            for task in category.tasks:
                task.category_id = None
        
        db.session.delete(category)
        db.session.commit()
        
        return None, 204

    @staticmethod
    def update_category(user_id, category_id, data):
        category = Category.query.filter_by(
            id=category_id,
            user_id=user_id
        ).first()

        if not category:
            return {'error': 'Category not found'}, 404

        # Ensure unique name per user when renaming
        new_name = data.get('name')
        if new_name and new_name != category.name:
            existing = Category.query.filter_by(user_id=user_id, name=new_name).first()
            if existing:
                return {'error': 'Category with this name already exists'}, 409
            category.name = new_name

        if 'color' in data and data.get('color'):
            category.color = data.get('color')

        db.session.commit()
        return category.to_dict(), 200