# ABOUTME: API blueprint initialization for MediaMTX integration and admin endpoints
# ABOUTME: Provides external auth webhook and customer management APIs

from flask import Blueprint

api_bp = Blueprint('api', __name__)

from app.api import routes, mediamtx
