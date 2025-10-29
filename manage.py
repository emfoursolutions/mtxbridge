# ABOUTME: CLI management script for database migrations and admin tasks
# ABOUTME: Provides commands for initializing DB, creating admins, and other operations

import os
import click
from flask.cli import FlaskGroup
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.models.user import User
from app.models.customer import Customer
from app.models.api_key import ApiKey

def create_cli_app():
    """Create app instance for CLI"""
    return create_app(os.environ.get('FLASK_ENV', 'development'))

cli = FlaskGroup(create_app=create_cli_app)


@cli.command('init-db')
def init_db():
    """Initialize the database"""
    db.create_all()
    click.echo('Database initialized successfully!')


@cli.command('create-admin')
@click.argument('username')
@click.option('--email', prompt='Email')
@click.option('--display-name', prompt='Display Name')
def create_admin(username, email, display_name):
    """Create an admin user"""
    user = User.query.filter_by(username=username).first()

    if user:
        click.echo(f'User {username} already exists!')
        return

    user = User(
        username=username,
        email=email,
        display_name=display_name,
        is_admin=True,
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    click.echo(f'Admin user {username} created successfully!')


@cli.command('list-users')
def list_users():
    """List all users"""
    users = User.query.all()

    if not users:
        click.echo('No users found.')
        return

    click.echo('\nUsers:')
    click.echo('-' * 80)
    for user in users:
        status = 'Active' if user.is_active else 'Inactive'
        role = 'Admin' if user.is_admin else 'User'
        click.echo(f'{user.id:4d} | {user.username:20s} | {user.email:30s} | {role:6s} | {status}')
    click.echo('-' * 80)


@cli.command('list-customers')
def list_customers():
    """List all customers"""
    customers = Customer.query.all()

    if not customers:
        click.echo('No customers found.')
        return

    click.echo('\nCustomers:')
    click.echo('-' * 80)
    for customer in customers:
        status = 'Active' if customer.is_active else 'Inactive'
        key_count = customer.api_keys.count()
        click.echo(f'{customer.id:4d} | {customer.name:25s} | {customer.email:30s} | Keys: {key_count} | {status}')
    click.echo('-' * 80)


if __name__ == '__main__':
    cli()
