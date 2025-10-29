# ABOUTME: End-to-end tests for complete customer management workflow
# ABOUTME: Tests full flow from customer creation to API key usage and revocation

import pytest
import json
from app.services.customer_service import CustomerService
from app.services.api_key_service import ApiKeyService


class TestCustomerWorkflow:
    """Test complete customer management workflow"""

    def test_complete_customer_lifecycle(self, client, db_session):
        """Test full customer lifecycle: create, add key, use key, revoke, delete"""

        # Step 1: Create customer
        customer = CustomerService.create_customer(
            name='E2E Test Customer',
            email='e2e@example.com',
            organization='E2E Org'
        )
        assert customer.id is not None
        assert customer.is_active is True

        # Step 2: Create API key for customer
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=customer.id,
            name='E2E Test Key',
            can_publish=True,
            can_read=True
        )
        assert api_key.id is not None
        assert plaintext.startswith('mtx_')

        # Step 3: Use API key to authenticate for stream access
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is True
        assert data['customer_id'] == customer.id

        # Step 4: Test publish permission
        response = client.post('/api/mediamtx/auth', json={
            'action': 'publish',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 200

        # Step 5: Revoke API key
        result = ApiKeyService.revoke_api_key(api_key.id)
        assert result is True

        # Step 6: Try to use revoked key (should fail)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 401

        # Step 7: Deactivate customer
        result = CustomerService.deactivate_customer(customer.id)
        assert result is True
        assert customer.is_active is False

        # Step 8: Delete customer
        result = CustomerService.delete_customer(customer.id)
        assert result is True
        assert CustomerService.get_customer_by_id(customer.id) is None

    def test_multiple_keys_workflow(self, client, db_session):
        """Test customer with multiple API keys"""

        # Create customer
        customer = CustomerService.create_customer(
            name='Multi-Key Customer',
            email='multikey@example.com'
        )

        # Create multiple keys with different permissions
        read_key, read_plaintext = ApiKeyService.create_api_key(
            customer_id=customer.id,
            name='Read Only Key',
            can_publish=False,
            can_read=True
        )

        publish_key, publish_plaintext = ApiKeyService.create_api_key(
            customer_id=customer.id,
            name='Publish Key',
            can_publish=True,
            can_read=True
        )

        # Test read-only key for reading (should succeed)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'query': f'api_key={read_plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 200

        # Test read-only key for publishing (should fail)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'publish',
            'path': 'test/stream',
            'query': f'api_key={read_plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 403

        # Test publish key for publishing (should succeed)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'publish',
            'path': 'test/stream',
            'query': f'api_key={publish_plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 200

        # Verify both keys exist
        keys = ApiKeyService.get_customer_keys(customer.id)
        assert len(keys) == 2

    def test_key_expiration_workflow(self, client, db_session):
        """Test API key expiration"""
        from datetime import datetime, timedelta

        # Create customer
        customer = CustomerService.create_customer(
            name='Expiry Test Customer',
            email='expiry@example.com'
        )

        # Create key with expiration
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=customer.id,
            name='Expiring Key',
            can_read=True,
            expires_in_days=30
        )

        assert api_key.expires_at is not None
        assert api_key.is_valid() is True

        # Use key before expiration (should work)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 200

        # Manually expire the key
        api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        db_session.commit()

        assert api_key.is_valid() is False

        # Try to use expired key (should fail)
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })
        assert response.status_code == 401
