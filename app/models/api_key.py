# ABOUTME: API Key model for customer authentication to MediaMTX streams
# ABOUTME: Stores hashed keys and tracks usage for security and auditing

from datetime import datetime
import secrets
import hashlib
from app import db


class ApiKey(db.Model):
    """API key for customer authentication to MediaMTX"""

    __tablename__ = 'api_keys'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)  # Friendly name for the key
    key_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    key_prefix = db.Column(db.String(10), nullable=False)  # First few chars for identification
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

    # Stream permissions (could be expanded to per-stream granular permissions)
    can_publish = db.Column(db.Boolean, default=False, nullable=False)
    can_read = db.Column(db.Boolean, default=True, nullable=False)

    def __repr__(self):
        return f'<ApiKey {self.name} ({self.key_prefix}...)>'

    @staticmethod
    def generate_key(prefix='mtx_', length=32):
        """Generate a new random API key"""
        random_part = secrets.token_urlsafe(length)
        return f"{prefix}{random_part}"

    @staticmethod
    def hash_key(key):
        """Hash an API key using SHA-256"""
        return hashlib.sha256(key.encode()).hexdigest()

    def verify_key(self, key):
        """Verify if the provided key matches this API key"""
        return self.key_hash == self.hash_key(key)

    def update_last_used(self):
        """Update the last used timestamp"""
        self.last_used_at = datetime.utcnow()
        db.session.commit()

    def is_valid(self):
        """Check if the API key is valid (active and not expired)"""
        if not self.is_active:
            return False

        if self.expires_at and self.expires_at < datetime.utcnow():
            return False

        return True

    def to_dict(self, include_secret=False):
        """Convert API key to dictionary representation"""
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'key_prefix': self.key_prefix,
            'is_active': self.is_active,
            'can_publish': self.can_publish,
            'can_read': self.can_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }

        return data
