# ABOUTME: Quick SQLite database initialization script
# ABOUTME: Creates database and optionally creates an admin user

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Create instance directory FIRST (before importing app)
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_path, exist_ok=True)

# Don't set DATABASE_URL - let config.py handle it with absolute path

from app import create_app, db
from app.models.user import User

def init_sqlite_db():
    """Initialize SQLite database and optionally create admin user"""
    print("Initializing SQLite database...")

    app = create_app('development')

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created successfully!")

        # Check if we should create an admin user
        create_admin = input("\nCreate an admin user? (y/n): ").strip().lower()

        if create_admin == 'y':
            username = input("Username: ").strip()
            email = input("Email: ").strip()
            display_name = input("Display Name: ").strip()

            # Check if user already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                print(f"✗ User '{username}' already exists!")
                sys.exit(1)

            # Create admin user
            user = User(
                username=username,
                email=email,
                display_name=display_name,
                is_admin=True,
                is_active=True
            )

            db.session.add(user)
            db.session.commit()

            print(f"✓ Admin user '{username}' created successfully!")
            print("\nNOTE: This user will authenticate via LDAP/AD.")
            print("Make sure the username matches your LDAP/AD username.")

        print("\n" + "="*60)
        print("Database initialization complete!")
        print("="*60)
        print(f"\nDatabase location: {os.path.abspath('instance/mtxman.db')}")
        print("\nYou can now run the application with:")
        print("  python app.py")
        print("\nOr with docker-compose:")
        print("  docker-compose up")


if __name__ == '__main__':
    init_sqlite_db()
