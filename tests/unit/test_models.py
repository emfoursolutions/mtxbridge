# ABOUTME: Unit tests for database models
# ABOUTME: Tests model creation, relationships, and methods

import pytest
from datetime import datetime, timedelta
from app.models.user import User
from app.models.customer import Customer
from app.models.api_key import ApiKey


class TestUserModel:
    """Test User model"""

    def test_create_user(self, db_session):
        """Test creating a user"""
        user = User(
            username='newuser',
            email='newuser@example.com',
            display_name='New User',
            is_active=True
        )
        db_session.add(user)
        db_session.commit()

        assert user.id is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@example.com'
        assert user.is_active is True
        assert user.is_admin is False

    def test_user_repr(self, sample_user):
        """Test user string representation"""
        assert repr(sample_user) == '<User testuser>'

    def test_update_last_login(self, db_session, sample_user):
        """Test updating last login timestamp"""
        original_login = sample_user.last_login
        sample_user.update_last_login()

        assert sample_user.last_login is not None
        assert sample_user.last_login != original_login

    def test_user_to_dict(self, sample_user):
        """Test user to dictionary conversion"""
        user_dict = sample_user.to_dict()

        assert user_dict['username'] == 'testuser'
        assert user_dict['email'] == 'test@example.com'
        assert user_dict['is_active'] is True
        assert user_dict['is_admin'] is False


class TestCustomerModel:
    """Test Customer model"""

    def test_create_customer(self, db_session):
        """Test creating a customer"""
        customer = Customer(
            name='New Customer',
            email='new@example.com',
            organization='New Org'
        )
        db_session.add(customer)
        db_session.commit()

        assert customer.id is not None
        assert customer.name == 'New Customer'
        assert customer.email == 'new@example.com'
        assert customer.is_active is True

    def test_customer_repr(self, sample_customer):
        """Test customer string representation"""
        assert repr(sample_customer) == '<Customer Test Customer (customer@example.com)>'

    def test_customer_to_dict(self, sample_customer):
        """Test customer to dictionary conversion"""
        customer_dict = sample_customer.to_dict()

        assert customer_dict['name'] == 'Test Customer'
        assert customer_dict['email'] == 'customer@example.com'
        assert customer_dict['organization'] == 'Test Org'
        assert customer_dict['is_active'] is True

    def test_customer_api_keys_relationship(self, db_session, sample_customer):
        """Test customer API keys relationship"""
        api_key = ApiKey(
            customer_id=sample_customer.id,
            name='Test Key',
            key_hash='abc123',
            key_prefix='mtx_test'
        )
        db_session.add(api_key)
        db_session.commit()

        assert sample_customer.api_keys.count() == 1
        assert sample_customer.api_keys.first().name == 'Test Key'

    def test_get_active_keys(self, db_session, sample_customer):
        """Test getting active keys only"""
        active_key = ApiKey(
            customer_id=sample_customer.id,
            name='Active Key',
            key_hash='active123',
            key_prefix='mtx_act',
            is_active=True
        )
        inactive_key = ApiKey(
            customer_id=sample_customer.id,
            name='Inactive Key',
            key_hash='inactive123',
            key_prefix='mtx_ina',
            is_active=False
        )
        db_session.add_all([active_key, inactive_key])
        db_session.commit()

        active_keys = sample_customer.get_active_keys()
        assert len(active_keys) == 1
        assert active_keys[0].name == 'Active Key'


class TestApiKeyModel:
    """Test ApiKey model"""

    def test_generate_key(self):
        """Test API key generation"""
        key = ApiKey.generate_key(prefix='test_', length=32)

        assert key.startswith('test_')
        assert len(key) > 40

    def test_hash_key(self):
        """Test API key hashing"""
        key = 'test_key_123'
        hash1 = ApiKey.hash_key(key)
        hash2 = ApiKey.hash_key(key)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_verify_key(self, sample_api_key):
        """Test API key verification"""
        assert sample_api_key.verify_key(sample_api_key._plaintext) is True
        assert sample_api_key.verify_key('wrong_key') is False

    def test_is_valid_active_key(self, sample_api_key):
        """Test valid active key"""
        assert sample_api_key.is_valid() is True

    def test_is_valid_inactive_key(self, db_session, sample_api_key):
        """Test invalid inactive key"""
        sample_api_key.is_active = False
        db_session.commit()

        assert sample_api_key.is_valid() is False

    def test_is_valid_expired_key(self, db_session, sample_api_key):
        """Test invalid expired key"""
        sample_api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()

        assert sample_api_key.is_valid() is False

    def test_update_last_used(self, db_session, sample_api_key):
        """Test updating last used timestamp"""
        original_last_used = sample_api_key.last_used_at
        sample_api_key.update_last_used()

        assert sample_api_key.last_used_at is not None
        assert sample_api_key.last_used_at != original_last_used

    def test_api_key_to_dict(self, sample_api_key):
        """Test API key to dictionary conversion"""
        key_dict = sample_api_key.to_dict()

        assert key_dict['name'] == 'Test Key'
        assert key_dict['can_publish'] is True
        assert key_dict['can_read'] is True
        assert key_dict['is_active'] is True
