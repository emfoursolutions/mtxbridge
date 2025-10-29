# ABOUTME: Integration tests for MediaMTX external authentication webhook
# ABOUTME: Tests the complete auth flow for stream access validation

import pytest
import json
from app.services.api_key_service import ApiKeyService


class TestMediaMTXAuth:
    """Test MediaMTX authentication endpoint"""

    def test_auth_with_valid_key_in_query(self, client, db_session, sample_customer):
        """Test authentication with API key in query string"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Test Key',
            can_publish=True,
            can_read=True
        )

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
        assert data['customer_id'] == sample_customer.id

    def test_auth_with_valid_key_in_username(self, client, db_session, sample_customer):
        """Test authentication with API key as username"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Test Key',
            can_publish=True,
            can_read=True
        )

        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'user': plaintext,
            'ip': '127.0.0.1'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['authenticated'] is True

    def test_auth_with_invalid_key(self, client, db_session):
        """Test authentication with invalid API key"""
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': 'api_key=invalid_key_123',
            'ip': '127.0.0.1'
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_auth_with_no_key(self, client, db_session):
        """Test authentication without API key"""
        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'ip': '127.0.0.1'
        })

        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data

    def test_auth_publish_without_permission(self, client, db_session, sample_customer):
        """Test publish authentication without publish permission"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Read Only Key',
            can_publish=False,
            can_read=True
        )

        response = client.post('/api/mediamtx/auth', json={
            'action': 'publish',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })

        assert response.status_code == 403
        data = json.loads(response.data)
        assert 'error' in data

    def test_auth_with_inactive_customer(self, client, db_session, sample_customer):
        """Test authentication with inactive customer"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Test Key',
            can_read=True
        )

        sample_customer.is_active = False
        db_session.commit()

        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })

        assert response.status_code == 401

    def test_auth_with_inactive_key(self, client, db_session, sample_customer):
        """Test authentication with inactive API key"""
        api_key, plaintext = ApiKeyService.create_api_key(
            customer_id=sample_customer.id,
            name='Test Key',
            can_read=True
        )

        api_key.is_active = False
        db_session.commit()

        response = client.post('/api/mediamtx/auth', json={
            'action': 'read',
            'path': 'test/stream',
            'protocol': 'rtsp',
            'query': f'api_key={plaintext}',
            'ip': '127.0.0.1'
        })

        assert response.status_code == 401

    def test_webhook_event(self, client, db_session):
        """Test MediaMTX webhook event endpoint"""
        response = client.post('/api/mediamtx/webhook', json={
            'event': 'stream_started',
            'path': 'test/stream'
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['received'] is True
