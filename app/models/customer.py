# ABOUTME: Customer model representing external clients accessing MediaMTX
# ABOUTME: Each customer can have multiple API keys for stream authentication

from datetime import datetime
from app import db


class Customer(db.Model):
    """Customer entity with access to MediaMTX streams"""

    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    organization = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    api_keys = db.relationship('ApiKey', backref='customer', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name} ({self.email})>'

    def to_dict(self, include_keys=False):
        """Convert customer to dictionary representation"""
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'organization': self.organization,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_keys:
            data['api_keys'] = [key.to_dict() for key in self.api_keys.all()]

        return data

    def get_active_keys(self):
        """Get all active API keys for this customer"""
        return self.api_keys.filter_by(is_active=True).all()
