# ABOUTME: Integration tests for admin API routes
# ABOUTME: Tests customer and API key management endpoints

import pytest
import json
from flask_login import login_user
from app.services.customer_service import CustomerService
from app.services.api_key_service import ApiKeyService


class TestCustomerRoutes:
    """Test customer management routes"""

    def test_list_customers_unauthenticated(self, client):
        """Test listing customers without authentication"""
        response = client.get('/api/customers')
        assert response.status_code == 302  # Redirect to login

    def test_create_customer_unauthenticated(self, client):
        """Test creating customer without authentication"""
        response = client.post('/api/customers/create', data={
            'name': 'Test Customer',
            'email': 'test@example.com'
        })
        assert response.status_code == 302  # Redirect to login

    def test_view_customer_unauthenticated(self, client, sample_customer):
        """Test viewing customer without authentication"""
        response = client.get(f'/api/customers/{sample_customer.id}')
        assert response.status_code == 302  # Redirect to login


class TestApiKeyRoutes:
    """Test API key management routes"""

    def test_create_api_key_unauthenticated(self, client, sample_customer):
        """Test creating API key without authentication"""
        response = client.post(f'/api/customers/{sample_customer.id}/keys/create', data={
            'name': 'Test Key',
            'can_read': 'on'
        })
        assert response.status_code == 302  # Redirect to login

    def test_revoke_api_key_unauthenticated(self, client, sample_api_key):
        """Test revoking API key without authentication"""
        response = client.post(f'/api/api-keys/{sample_api_key.id}/revoke')
        assert response.status_code == 302  # Redirect to login


class TestRestApi:
    """Test REST API endpoints"""

    def test_api_list_customers_unauthenticated(self, client):
        """Test REST API list customers without auth"""
        response = client.get('/api/api/v1/customers')
        assert response.status_code == 302  # Redirect to login

    def test_api_get_customer_unauthenticated(self, client, sample_customer):
        """Test REST API get customer without auth"""
        response = client.get(f'/api/api/v1/customers/{sample_customer.id}')
        assert response.status_code == 302  # Redirect to login
