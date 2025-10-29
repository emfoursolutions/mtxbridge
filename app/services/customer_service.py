# ABOUTME: Service layer for customer management operations
# ABOUTME: Handles customer CRUD operations and business logic

from typing import Optional, List
from app import db
from app.models.customer import Customer


class CustomerService:
    """Service for managing customers"""

    @staticmethod
    def create_customer(name: str, email: str, organization: Optional[str] = None) -> Customer:
        """Create a new customer"""
        customer = Customer(
            name=name,
            email=email,
            organization=organization
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        return Customer.query.get(customer_id)

    @staticmethod
    def get_customer_by_email(email: str) -> Optional[Customer]:
        """Get customer by email"""
        return Customer.query.filter_by(email=email).first()

    @staticmethod
    def get_all_customers(active_only: bool = False) -> List[Customer]:
        """Get all customers, optionally filtered by active status"""
        query = Customer.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Customer.created_at.desc()).all()

    @staticmethod
    def update_customer(customer_id: int, **kwargs) -> Optional[Customer]:
        """Update customer attributes"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return None

        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)

        db.session.commit()
        return customer

    @staticmethod
    def deactivate_customer(customer_id: int) -> bool:
        """Deactivate a customer and all their API keys"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return False

        customer.is_active = False

        # Deactivate all API keys
        for api_key in customer.api_keys:
            api_key.is_active = False

        db.session.commit()
        return True

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        """Delete a customer permanently"""
        customer = Customer.query.get(customer_id)
        if not customer:
            return False

        db.session.delete(customer)
        db.session.commit()
        return True
