from flask import g
from app.models.task import Task
from app.models.category import Category
from app.database import db
from datetime import datetime
import uuid

class TaskService:
    
    @staticmethod
    def get_tasks(filters, pagination):
        query = Task.query.filter_by(
            user_id=g.current_user.id,
            deleted_at=None
        )
        
        # Apply filters
        if filters.get('status'):
            query = query.filter_by(status=filters['status'])
        
        if filters.get('priority'):
            query = query.filter_by(priority=filters['priority'])
        
        if filters.get('category_id'):
            query = query.filter_by(category_id=filters['category_id'])
        
        # Pagination
        page = pagination.get('page', 1)
        limit = pagination.get('limit', 10)
        
        total = query.count()
        tasks = query.order_by(Task.created_at.desc())\
                     .offset((page - 1) * limit)\
                     .limit(limit)\
                     .all()
        
        return {
            'data': [task.to_dict() for task in tasks],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }, 200
    
    @staticmethod
    def create_task(task_data):
        # Validate category if provided
        if 'category_id' in task_data and task_data['category_id'] is not None:
            category = Category.query.filter_by(
                id=task_data['category_id'],
                user_id=g.current_user.id
            ).first()
            
            if not category:
                return {'error': 'Category not found'}, 404
        
        task = Task(
            id=str(uuid.uuid4()),
            title=task_data['title'],
            description=task_data.get('description'),
            priority=task_data.get('priority', 'medium'),
            due_date=task_data.get('due_date'),
            category_id=task_data.get('category_id'),
            user_id=g.current_user.id,
            status='todo'
        )
        
        db.session.add(task)
        db.session.commit()
        
        return task.to_dict(), 201
    
    @staticmethod
    def get_task(task_id):
        task = Task.query.filter_by(
            id=task_id,
            user_id=g.current_user.id,
            deleted_at=None
        ).first()
        
        if not task:
            return {'error': 'Task not found'}, 404
        
        return task.to_dict(), 200
    
    @staticmethod
    def update_task(task_id, task_data):
        task = Task.query.filter_by(
            id=task_id,
            user_id=g.current_user.id,
            deleted_at=None
        ).first()
        
        if not task:
            return {'error': 'Task not found'}, 404
        
        # Validate category if provided
        if 'category_id' in task_data and task_data['category_id'] is not None:
            category = Category.query.filter_by(
                id=task_data['category_id'],
                user_id=g.current_user.id
            ).first()
            
            if not category:
                return {'error': 'Category not found'}, 404
        
        # Update fields
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return task.to_dict(), 200
    
    @staticmethod
    def update_status(task_id, status_data):
        task = Task.query.filter_by(
            id=task_id,
            user_id=g.current_user.id,
            deleted_at=None
        ).first()
        
        if not task:
            return {'error': 'Task not found'}, 404
        
        # Validate status transition
        new_status = status_data['status']
        valid_transitions = {
            'todo': ['in_progress', 'done'],
            'in_progress': ['done', 'todo'],
            'done': ['archived', 'in_progress', 'todo'],
            'archived': ['todo', 'done']
        }
        
        if new_status not in valid_transitions.get(task.status, []):
            return {'error': f'Invalid status transition from {task.status} to {new_status}'}, 400
        
        task.status = new_status
        if new_status == 'done':
            task.completed_at = datetime.utcnow()
        else:
            task.completed_at = None
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return task.to_dict(), 200
    
    @staticmethod
    def delete_task(task_id):
        task = Task.query.filter_by(
            id=task_id,
            user_id=g.current_user.id,
            deleted_at=None
        ).first()
        
        if not task:
            return {'error': 'Task not found'}, 404
        
        # Soft delete
        task.deleted_at = datetime.utcnow()
        db.session.commit()
        
        return None, 204
    
    @staticmethod
    def search_tasks(query):
        tasks = Task.query.filter(
            Task.user_id == g.current_user.id,
            Task.deleted_at == None,
            Task.title.ilike(f'%{query}%')
        ).order_by(Task.created_at.desc()).all()
        
        return {'data': [task.to_dict() for task in tasks]}, 200
    
    @staticmethod
    def assign_task(task_id, assignee_id):
        task = Task.query.filter_by(
            id=task_id,
            user_id=g.current_user.id,
            deleted_at=None
        ).first()
        
        if not task:
            return {'error': 'Task not found'}, 404
        
        # Check if assignee exists
        from app.models.user import User
        assignee = db.session.get(User, assignee_id)
        
        if not assignee:
            return {'error': 'User not found'}, 404
        
        task.assigned_to = assignee_id
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return task.to_dict(), 200