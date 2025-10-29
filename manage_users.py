#!/usr/bin/env python3
# ABOUTME: CLI utility script for managing users directly in the database
# ABOUTME: Allows listing, promoting, demoting, activating, and deactivating users

import os
import sys
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models import User

def list_users():
    """List all users in the database"""
    users = User.query.all()
    if not users:
        print("No users found in database.")
        return

    print("\n{:<5} {:<20} {:<30} {:<10} {:<10}".format("ID", "Username", "Email", "Admin", "Active"))
    print("-" * 85)
    for user in users:
        email = user.email or "N/A"
        admin = "Yes" if user.is_admin else "No"
        active = "Yes" if user.is_active else "No"
        print("{:<5} {:<20} {:<30} {:<10} {:<10}".format(
            user.id, user.username, email, admin, active
        ))
    print()

def promote_user(username):
    """Promote a user to admin"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    if user.is_admin:
        print(f"User '{username}' is already an admin.")
        return

    user.is_admin = True
    db.session.commit()
    print(f"Success: User '{username}' has been promoted to admin.")

def demote_user(username):
    """Remove admin privileges from a user"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    if not user.is_admin:
        print(f"User '{username}' is already not an admin.")
        return

    user.is_admin = False
    db.session.commit()
    print(f"Success: Admin privileges removed from user '{username}'.")

def activate_user(username):
    """Activate a user account"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    if user.is_active:
        print(f"User '{username}' is already active.")
        return

    user.is_active = True
    db.session.commit()
    print(f"Success: User '{username}' has been activated.")

def deactivate_user(username):
    """Deactivate a user account"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    if not user.is_active:
        print(f"User '{username}' is already inactive.")
        return

    user.is_active = False
    db.session.commit()
    print(f"Success: User '{username}' has been deactivated.")

def delete_user(username):
    """Delete a user from the database"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"Error: User '{username}' not found.")
        return

    confirm = input(f"Are you sure you want to delete user '{username}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Deletion cancelled.")
        return

    db.session.delete(user)
    db.session.commit()
    print(f"Success: User '{username}' has been deleted.")

def print_usage():
    """Print usage instructions"""
    print("""
Usage: python manage_users.py <command> [username]

Commands:
  list                  - List all users
  promote <username>    - Promote user to admin
  demote <username>     - Remove admin privileges from user
  activate <username>   - Activate user account
  deactivate <username> - Deactivate user account
  delete <username>     - Delete user from database

Examples:
  python manage_users.py list
  python manage_users.py promote john.doe
  python manage_users.py demote jane.smith
  python manage_users.py activate john.doe
  python manage_users.py delete old.user
""")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # Create app context
    config_name = os.environ.get('FLASK_ENV', 'development')
    app = create_app(config_name)

    with app.app_context():
        command = sys.argv[1].lower()

        if command == 'list':
            list_users()
        elif command in ['promote', 'demote', 'activate', 'deactivate', 'delete']:
            if len(sys.argv) < 3:
                print(f"Error: {command} command requires a username.")
                print_usage()
                sys.exit(1)

            username = sys.argv[2]

            if command == 'promote':
                promote_user(username)
            elif command == 'demote':
                demote_user(username)
            elif command == 'activate':
                activate_user(username)
            elif command == 'deactivate':
                deactivate_user(username)
            elif command == 'delete':
                delete_user(username)
        else:
            print(f"Error: Unknown command '{command}'")
            print_usage()
            sys.exit(1)

if __name__ == '__main__':
    main()
