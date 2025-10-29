# ABOUTME: Configuration classes for different deployment environments
# ABOUTME: Loads settings from environment variables with sensible defaults

import os
from datetime import timedelta
from pathlib import Path

# Get the base directory
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration with common settings"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'mtxman.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Engine options - only use pooling for PostgreSQL
    # SQLite doesn't support connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {}

    # LDAP Configuration
    LDAP_HOST = os.environ.get('LDAP_HOST', 'ldap://localhost')
    LDAP_PORT = int(os.environ.get('LDAP_PORT', 389))
    LDAP_USE_SSL = os.environ.get('LDAP_USE_SSL', 'False').lower() == 'true'
    LDAP_BASE_DN = os.environ.get('LDAP_BASE_DN', 'dc=example,dc=com')
    LDAP_USER_DN = os.environ.get('LDAP_USER_DN', 'ou=users,dc=example,dc=com')
    LDAP_GROUP_DN = os.environ.get('LDAP_GROUP_DN', 'ou=groups,dc=example,dc=com')
    LDAP_BIND_USER_DN = os.environ.get('LDAP_BIND_USER_DN')
    LDAP_BIND_USER_PASSWORD = os.environ.get('LDAP_BIND_USER_PASSWORD')
    LDAP_USER_SEARCH_SCOPE = os.environ.get('LDAP_USER_SEARCH_SCOPE', 'SUBTREE')
    LDAP_USER_OBJECT_FILTER = os.environ.get('LDAP_USER_OBJECT_FILTER', '(objectClass=person)')
    LDAP_USER_RDN_ATTR = os.environ.get('LDAP_USER_RDN_ATTR', 'cn')
    LDAP_USER_LOGIN_ATTR = os.environ.get('LDAP_USER_LOGIN_ATTR', 'sAMAccountName')

    # MediaMTX
    MEDIAMTX_WEBHOOK_SECRET = os.environ.get('MEDIAMTX_WEBHOOK_SECRET', 'change-me')
    MEDIAMTX_BASE_URL = os.environ.get('MEDIAMTX_BASE_URL', 'http://localhost:8554')

    # API Keys
    API_KEY_LENGTH = int(os.environ.get('API_KEY_LENGTH', 32))
    API_KEY_PREFIX = os.environ.get('API_KEY_PREFIX', 'mtx_')

    # Session
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(
        seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 3600))
    )

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/mtxman.log')


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False

    # Enforce secure session cookies in production
    SESSION_COOKIE_SECURE = True

    # Production should use PostgreSQL with connection pooling
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }


config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
