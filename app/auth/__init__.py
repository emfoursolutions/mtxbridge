# ABOUTME: Authentication blueprint initialization
# ABOUTME: Handles LDAP/AD login, logout, and session management

from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
