# ABOUTME: Pytest configuration and shared fixtures for all tests
# ABOUTME: Sets up test database, app context, and common test data

import pytest
from app import create_app, db
from app.models.user import User
from app.models.customer import Customer
from app.models.api_key import ApiKey


@pytest.fixture(scope='session')
def app():
    """Create application for testing"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Create database session for testing"""
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()

        options = dict(bind=connection, binds={})
        session = db.create_scoped_session(options=options)

        db.session = session

        yield session

        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing"""
    user = User(
        username='testuser',
        email='test@example.com',
        display_name='Test User',
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_admin(db_session):
    """Create a sample admin user for testing"""
    admin = User(
        username='admin',
        email='admin@example.com',
        display_name='Admin User',
        is_active=True,
        is_admin=True
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def sample_customer(db_session):
    """Create a sample customer for testing"""
    customer = Customer(
        name='Test Customer',
        email='customer@example.com',
        organization='Test Org',
        is_active=True
    )
    db_session.add(customer)
    db_session.commit()
    return customer


@pytest.fixture
def sample_api_key(db_session, sample_customer):
    """Create a sample API key for testing"""
    from app.services.api_key_service import ApiKeyService

    api_key, plaintext = ApiKeyService.create_api_key(
        customer_id=sample_customer.id,
        name='Test Key',
        can_publish=True,
        can_read=True
    )

    # Store plaintext for testing
    api_key._plaintext = plaintext

    return api_key
