# ABOUTME: Unit tests for service layer business logic
# ABOUTME: Tests customer and API key service operations

import pytest
from app.services.customer_service import CustomerService
from app.services.api_key_service import ApiKeyService
from app.models.customer import Customer
from app.models.api_key import ApiKey


class TestCustomerService:
    """Test CustomerService"""

    def test_create_customer(self, db_session):
        """Test creating a customer via service"""
        customer = CustomerService.create_customer(
            name='Service Customer',
            email='service@example.com',
            organization='Service Org'
        )

        assert customer.id is not None
        assert customer.name == 'Service Customer'
        assert customer.email == 'service@example.com'
        assert customer.organization == 'Service Org'

    def test_get_customer_by_id(self, db_session, sample_customer):
        """Test getting customer by ID"""
        customer = CustomerService.get_customer_by_id(sample_customer.id)

        assert customer is not None
        assert customer.id == sample_customer.id
        assert customer.email == sample_customer.email

    def test_get_customer_by_email(self, db_session, sample_customer):
        """Test getting customer by email"""
        customer = CustomerService.get_customer_by_email(sample_customer.email)

        assert customer is not None
        assert customer.id == sample_customer.id

    def test_get_all_customers(self, db_session, sample_customer):
        """Test getting all customers"""
        customers = CustomerService.get_all_customers()

        assert len(customers) >= 1
        assert any(c.id == sample_customer.id for c in customers)

    def test_update_customer(self, db_session, sample_customer):
        """Test updating customer"""
        updated = CustomerService.update_customer(
            sample_customer.id,
            name='Updated Name',
            organization='Updated Org'
        )

        assert updated.name == 'Updated Name'
        assert updated.organization == 'Updated Org'

    def test_deactivate_customer(self, db_session, sample_customer, sample_api_key):
        """Test deactivating customer and their keys"""
        result = CustomerService.deactivate_customer(sample_customer.id)

        assert result is True
        assert sample_customer.is_active is False
        assert sample_api_key.is_active is False

    def test_delete_customer(self, db_session, sample_customer):
        """Test deleting customer"""
        customer_id = sample_customer.id
        result = CustomerService.delete_customer(customer_id)

        assert result is True
        assert CustomerService.get_customer_by_id(customer_id) is None


class TestApiKeyService:
    """Test ApiKeyService"""

    def test_create_api_key(self, db_session, sample_customer):
        """Test creating API key via service"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='New Key',
            can_publish=True,
            can_read=True
        )

        assert api_key.id is not None
        assert api_key.name == 'New Key'
        assert api_key.can_publish is True
        assert api_key.can_read is True
        assert plaintext.startswith('mtx_')

    def test_create_api_key_with_expiration(self, db_session, sample_customer):
        """Test creating API key with expiration"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Expiring Key',
            expires_in_days=30
        )

        assert api_key.expires_at is not None

    def test_verify_api_key_valid(self, db_session, sample_api_key):
        """Test verifying valid API key"""
        verified = ApiKeyService.verify_api_key(sample_api_key._plaintext)

        assert verified is not None
        assert verified.id == sample_api_key.id

    def test_verify_api_key_invalid(self, db_session):
        """Test verifying invalid API key"""
        verified = ApiKeyService.verify_api_key('invalid_key')

        assert verified is None

    def test_get_customer_keys(self, db_session, sample_customer, sample_api_key):
        """Test getting customer keys"""
        keys = ApiKeyService.get_customer_keys(sample_customer.id)

        assert len(keys) >= 1
        assert any(k.id == sample_api_key.id for k in keys)

    def test_revoke_api_key(self, db_session, sample_api_key):
        """Test revoking API key"""
        result = ApiKeyService.revoke_api_key(sample_api_key.id)

        assert result is True
        assert sample_api_key.is_active is False

    def test_delete_api_key(self, db_session, sample_api_key):
        """Test deleting API key"""
        key_id = sample_api_key.id
        result = ApiKeyService.delete_api_key(key_id)

        assert result is True
        assert ApiKeyService.get_api_key_by_id(key_id) is None

    def test_check_permission_publish(self, db_session, sample_api_key):
        """Test checking publish permission"""
        assert ApiKeyService.check_permission(sample_api_key, 'publish') is True

    def test_check_permission_read(self, db_session, sample_api_key):
        """Test checking read permission"""
        assert ApiKeyService.check_permission(sample_api_key, 'read') is True

    def test_check_permission_inactive_key(self, db_session, sample_api_key):
        """Test permission check on inactive key"""
        sample_api_key.is_active = False
        db_session.commit()

        assert ApiKeyService.check_permission(sample_api_key, 'read') is False
