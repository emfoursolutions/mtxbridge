# ABOUTME: MediaMTX external authentication webhook endpoint
# ABOUTME: Validates API keys for stream publish/read access via MediaMTX callbacks

import hmac
import hashlib
from flask import request, jsonify, current_app
from app.api import api_bp
from app.services.api_key_service import ApiKeyService
from app.models.customer import Customer


def verify_webhook_signature(payload, signature):
    """Verify HMAC signature from MediaMTX"""
    secret = current_app.config['MEDIAMTX_WEBHOOK_SECRET']
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


@api_bp.route('/mediamtx/auth', methods=['POST'])
def mediamtx_auth():
    """
    MediaMTX external authentication webhook

    Expected payload from MediaMTX:
    {
        "action": "publish" or "read",
        "path": "stream/path",
        "protocol": "rtsp/rtmp/hls/webrtc",
        "query": "api_key=xxx",
        "user": "username",
        "password": "password",
        "ip": "client_ip"
    }

    Response:
    200 OK - Authentication successful
    401 Unauthorized - Authentication failed
    """
    # Verify webhook signature if configured
    signature = request.headers.get('X-MediaMTX-Signature')
    if signature and current_app.config.get('MEDIAMTX_WEBHOOK_SECRET'):
        if not verify_webhook_signature(request.data, signature):
            current_app.logger.warning('MediaMTX webhook signature verification failed')
            return jsonify({'error': 'Invalid signature'}), 401

    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    action = data.get('action')  # 'publish' or 'read'
    query = data.get('query', '')
    user = data.get('user')
    password = data.get('password')
    ip = data.get('ip')
    path = data.get('path')

    # Try to extract API key from various sources
    api_key_value = None

    # 1. Check query string
    if 'api_key=' in query:
        api_key_value = query.split('api_key=')[1].split('&')[0]

    # 2. Check username (API key as username)
    elif user and user.startswith('mtx_'):
        api_key_value = user

    # 3. Check password (API key as password)
    elif password and password.startswith('mtx_'):
        api_key_value = password

    if not api_key_value:
        current_app.logger.warning(f'No API key provided for {action} request from {ip}')
        return jsonify({'error': 'No API key provided'}), 401

    # Verify API key
    api_key = ApiKeyService.verify_api_key(api_key_value)

    if not api_key:
        current_app.logger.warning(f'Invalid API key for {action} request from {ip}')
        return jsonify({'error': 'Invalid API key'}), 401

    # Check if customer is active
    if not api_key.customer.is_active:
        current_app.logger.warning(f'Inactive customer {api_key.customer.email} attempted {action} from {ip}')
        return jsonify({'error': 'Customer account is inactive'}), 401

    # Check permissions
    if not ApiKeyService.check_permission(api_key, action):
        current_app.logger.warning(
            f'API key {api_key.key_prefix}... lacks {action} permission (customer: {api_key.customer.email})'
        )
        return jsonify({'error': f'No permission to {action}'}), 403

    # Authentication successful
    current_app.logger.info(
        f'Authenticated {action} for customer {api_key.customer.email} '
        f'(key: {api_key.key_prefix}..., path: {path}, ip: {ip})'
    )

    return jsonify({
        'authenticated': True,
        'customer_id': api_key.customer.id,
        'customer_name': api_key.customer.name,
    }), 200


@api_bp.route('/mediamtx/webhook', methods=['POST'])
def mediamtx_webhook():
    """
    MediaMTX general webhook for events

    Can be used to track stream events like:
    - Stream started
    - Stream stopped
    - Reader connected
    - Reader disconnected
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    event_type = data.get('event')
    current_app.logger.info(f'MediaMTX webhook event: {event_type}')

    # Here you could implement event tracking, analytics, etc.
    # For now, just log and acknowledge

    return jsonify({'received': True}), 200
