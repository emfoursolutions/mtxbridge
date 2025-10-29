# ABOUTME: LDAP/AD authentication service using ldap3 library
# ABOUTME: Handles LDAP connection, user authentication, and user info retrieval

from typing import Optional, Dict
from ldap3 import Server, Connection, ALL, SUBTREE
from ldap3.core.exceptions import LDAPException
from flask import current_app


class LDAPService:
    """Service for LDAP/AD authentication"""

    @staticmethod
    def _get_ldap_config():
        """Get LDAP configuration from Flask app config"""
        return {
            'host': current_app.config.get('LDAP_HOST'),
            'port': current_app.config.get('LDAP_PORT', 389),
            'use_ssl': current_app.config.get('LDAP_USE_SSL', False),
            'base_dn': current_app.config.get('LDAP_BASE_DN'),
            'user_dn': current_app.config.get('LDAP_USER_DN'),
            'bind_user_dn': current_app.config.get('LDAP_BIND_USER_DN'),
            'bind_password': current_app.config.get('LDAP_BIND_USER_PASSWORD'),
            'user_search_scope': current_app.config.get('LDAP_USER_SEARCH_SCOPE', 'SUBTREE'),
            'user_object_filter': current_app.config.get('LDAP_USER_OBJECT_FILTER', '(objectClass=person)'),
            'user_login_attr': current_app.config.get('LDAP_USER_LOGIN_ATTR', 'sAMAccountName'),
        }

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """
        Authenticate user against LDAP/AD server

        Returns:
            Dictionary with user info if successful, None if failed
        """
        if not username or not password:
            return None

        config = LDAPService._get_ldap_config()

        try:
            # Create LDAP server object
            server = Server(
                config['host'],
                port=config['port'],
                use_ssl=config['use_ssl'],
                get_info=ALL
            )

            # First, bind with service account to search for user
            if config['bind_user_dn'] and config['bind_password']:
                conn = Connection(
                    server,
                    user=config['bind_user_dn'],
                    password=config['bind_password'],
                    auto_bind=True
                )
            else:
                # Try anonymous bind
                conn = Connection(server, auto_bind=True)

            # Search for user
            search_filter = f"(&{config['user_object_filter']}({config['user_login_attr']}={username}))"
            search_base = config['user_dn'] or config['base_dn']

            conn.search(
                search_base=search_base,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=['cn', 'mail', 'displayName', 'distinguishedName']
            )

            if not conn.entries:
                current_app.logger.warning(f"LDAP user not found: {username}")
                return None

            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn

            # Close the service account connection
            conn.unbind()

            # Now try to bind as the user to verify password
            user_conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )

            if not user_conn.bound:
                current_app.logger.warning(f"LDAP authentication failed for: {username}")
                return None

            # Authentication successful, extract user info
            email = None
            if hasattr(user_entry, 'mail'):
                email_value = str(user_entry.mail)
                # Handle empty arrays or empty strings from LDAP
                if email_value and email_value not in ('[]', '', '[ ]'):
                    email = email_value

            user_info = {
                'username': username,
                'dn': user_dn,
                'email': email,
                'display_name': str(user_entry.displayName) if hasattr(user_entry, 'displayName') else str(user_entry.cn),
            }

            user_conn.unbind()

            current_app.logger.info(f"LDAP authentication successful for: {username}")
            return user_info

        except LDAPException as e:
            current_app.logger.error(f"LDAP error during authentication: {e}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected error during LDAP authentication: {e}")
            return None

    @staticmethod
    def test_connection() -> bool:
        """Test LDAP connection with current configuration"""
        config = LDAPService._get_ldap_config()

        try:
            server = Server(
                config['host'],
                port=config['port'],
                use_ssl=config['use_ssl'],
                get_info=ALL
            )

            if config['bind_user_dn'] and config['bind_password']:
                conn = Connection(
                    server,
                    user=config['bind_user_dn'],
                    password=config['bind_password'],
                    auto_bind=True
                )
            else:
                conn = Connection(server, auto_bind=True)

            result = conn.bound
            conn.unbind()
            return result

        except Exception as e:
            current_app.logger.error(f"LDAP connection test failed: {e}")
            return False
