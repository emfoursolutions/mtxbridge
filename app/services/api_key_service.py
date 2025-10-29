# ABOUTME: Service layer for API key generation and management
# ABOUTME: Handles key creation, validation, and permission checking

from typing import Optional, List, Tuple
from datetime import datetime, timedelta
from app import db
from app.models.api_key import ApiKey
from app.models.customer import Customer


class ApiKeyService:
    """Service for managing API keys"""

    @staticmethod
    def create_api_key(
        customer_id: int,
        name: str,
        can_publish: bool = False,
        can_read: bool = True,
        expires_in_days: Optional[int] = None
    ) -> Tuple[ApiKey, str]:
        """
        Create a new API key for a customer
        Returns tuple of (ApiKey object, plaintext key)
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Generate key
        plaintext_key = ApiKey.generate_key()
        key_hash = ApiKey.hash_key(plaintext_key)
        key_prefix = plaintext_key[:8]  # First 8 chars for identification

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create API key
        api_key = ApiKey(
            customer_id=customer_id,
            name=name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            can_publish=can_publish,
            can_read=can_read,
            expires_at=expires_at
        )

        db.session.add(api_key)
        db.session.commit()

        return api_key, plaintext_key

    @staticmethod
    def verify_api_key(plaintext_key: str) -> Optional[ApiKey]:
        """Verify an API key and return the ApiKey object if valid"""
        key_hash = ApiKey.hash_key(plaintext_key)
        api_key = ApiKey.query.filter_by(key_hash=key_hash).first()

        if not api_key:
            return None

        if not api_key.is_valid():
            return None

        # Update last used timestamp
        api_key.update_last_used()

        return api_key

    @staticmethod
    def get_api_key_by_id(key_id: int) -> Optional[ApiKey]:
        """Get API key by ID"""
        return ApiKey.query.get(key_id)

    @staticmethod
    def get_customer_keys(customer_id: int, active_only: bool = False) -> List[ApiKey]:
        """Get all API keys for a customer"""
        query = ApiKey.query.filter_by(customer_id=customer_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(ApiKey.created_at.desc()).all()

    @staticmethod
    def revoke_api_key(key_id: int) -> bool:
        """Revoke (deactivate) an API key"""
        api_key = ApiKey.query.get(key_id)
        if not api_key:
            return False

        api_key.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def delete_api_key(key_id: int) -> bool:
        """Delete an API key permanently"""
        api_key = ApiKey.query.get(key_id)
        if not api_key:
            return False

        db.session.delete(api_key)
        db.session.commit()
        return True

    @staticmethod
    def check_permission(api_key: ApiKey, action: str) -> bool:
        """Check if an API key has permission for a specific action"""
        if not api_key.is_valid():
            return False

        if action == 'publish':
            return api_key.can_publish
        elif action == 'read':
            return api_key.can_read

        return False
