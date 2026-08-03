from app.models.user import User
from app.database import db
from passlib.hash import pbkdf2_sha256 as pwd_context
from datetime import datetime

class UserService:
    
    @staticmethod
    def update_profile(user_id, data):
        user = db.session.get(User, user_id)
        
        if not user:
            return {'error': 'User not found'}, 404
        
        # Check if email is being updated and if it's already taken
        if data.get('email') and data['email'] != user.email:
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return {'error': 'Email already registered'}, 409
        
        for key, value in data.items():
            setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user.to_dict(), 200
    
    @staticmethod
    def change_password(user_id, data):
        user = db.session.get(User, user_id)
        
        if not user:
            return {'error': 'User not found'}, 404
        
        # Verify current password
        if not pwd_context.verify(data['current_password'], user.password):
            return {'error': 'Current password is incorrect'}, 401
        
        # Hash and set new password
        user.password = pwd_context.hash(data['new_password'])
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {'message': 'Password changed successfully'}, 200