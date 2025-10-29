# ABOUTME: Service layer for user management operations
# ABOUTME: Handles user CRUD operations and admin functions

from typing import Optional, List
from app import db
from app.models.user import User


class UserService:
    """Service for managing users"""

    @staticmethod
    def create_user(
        username: str,
        email: Optional[str] = None,
        display_name: Optional[str] = None,
        dn: Optional[str] = None,
        is_admin: bool = False,
        is_active: bool = True
    ) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            display_name=display_name,
            dn=dn,
            is_admin=is_admin,
            is_active=is_active
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_all_users(active_only: bool = False) -> List[User]:
        """Get all users, optionally filtered by active status"""
        query = User.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(User.created_at.desc()).all()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> Optional[User]:
        """Update user attributes"""
        user = User.query.get(user_id)
        if not user:
            return None

        # Only allow certain fields to be updated
        allowed_fields = ['email', 'display_name', 'is_active', 'is_admin']
        for key, value in kwargs.items():
            if key in allowed_fields and hasattr(user, key):
                setattr(user, key, value)

        db.session.commit()
        return user

    @staticmethod
    def toggle_admin(user_id: int) -> Optional[User]:
        """Toggle admin status for a user"""
        user = User.query.get(user_id)
        if not user:
            return None

        user.is_admin = not user.is_admin
        db.session.commit()
        return user

    @staticmethod
    def toggle_active(user_id: int) -> Optional[User]:
        """Toggle active status for a user"""
        user = User.query.get(user_id)
        if not user:
            return None

        user.is_active = not user.is_active
        db.session.commit()
        return user

    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Deactivate a user"""
        user = User.query.get(user_id)
        if not user:
            return False

        user.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user permanently (use with caution)"""
        user = User.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def get_or_create_from_ldap(ldap_user_info: dict) -> User:
        """Get existing user or create from LDAP authentication data"""
        username = ldap_user_info.get('username')
        user = User.query.filter_by(username=username).first()

        if not user:
            user = User(
                username=username,
                email=ldap_user_info.get('email'),
                display_name=ldap_user_info.get('display_name'),
                dn=ldap_user_info.get('dn'),
            )
            db.session.add(user)
            db.session.commit()

        return user
