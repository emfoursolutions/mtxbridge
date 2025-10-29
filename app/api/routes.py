# ABOUTME: Admin API routes for customer and API key management
# ABOUTME: Provides CRUD operations for managing customers and their access keys

from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.api import api_bp
from app.auth.decorators import admin_required
from app.services.customer_service import CustomerService
from app.services.api_key_service import ApiKeyService
from app.services.user_service import UserService


@api_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard showing customers and statistics"""
    customers = CustomerService.get_all_customers()
    return render_template('dashboard.html', customers=customers)


# Customer Management Routes

@api_bp.route('/customers', methods=['GET'])
@login_required
def list_customers():
    """List all customers"""
    customers = CustomerService.get_all_customers()
    return render_template('customers/list.html', customers=customers)


@api_bp.route('/customers/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_customer():
    """Create a new customer"""
    if request.method == 'POST':
        data = request.form
        try:
            customer = CustomerService.create_customer(
                name=data['name'],
                email=data['email'],
                organization=data.get('organization')
            )
            flash(f'Customer {customer.name} created successfully!', 'success')
            return redirect(url_for('api.view_customer', customer_id=customer.id))
        except Exception as e:
            flash(f'Error creating customer: {str(e)}', 'danger')

    return render_template('customers/create.html')


@api_bp.route('/customers/<int:customer_id>', methods=['GET'])
@login_required
def view_customer(customer_id):
    """View customer details and API keys"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('api.list_customers'))

    api_keys = ApiKeyService.get_customer_keys(customer_id)
    return render_template('customers/view.html', customer=customer, api_keys=api_keys)


@api_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_customer(customer_id):
    """Edit customer details"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('api.list_customers'))

    if request.method == 'POST':
        data = request.form
        try:
            CustomerService.update_customer(
                customer_id,
                name=data.get('name'),
                email=data.get('email'),
                organization=data.get('organization'),
                is_active=data.get('is_active', 'off') == 'on'
            )
            flash(f'Customer {customer.name} updated successfully!', 'success')
            return redirect(url_for('api.view_customer', customer_id=customer_id))
        except Exception as e:
            flash(f'Error updating customer: {str(e)}', 'danger')

    return render_template('customers/edit.html', customer=customer)


@api_bp.route('/customers/<int:customer_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_customer(customer_id):
    """Deactivate a customer"""
    if CustomerService.deactivate_customer(customer_id):
        flash('Customer deactivated successfully', 'success')
    else:
        flash('Error deactivating customer', 'danger')
    return redirect(url_for('api.view_customer', customer_id=customer_id))


# API Key Management Routes

@api_bp.route('/customers/<int:customer_id>/keys/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_api_key(customer_id):
    """Create a new API key for a customer"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        flash('Customer not found', 'danger')
        return redirect(url_for('api.list_customers'))

    if request.method == 'POST':
        data = request.form
        try:
            api_key, plaintext = ApiKeyService.create_api_key(
                customer_id=customer_id,
                name=data['name'],
                can_publish=data.get('can_publish', 'off') == 'on',
                can_read=data.get('can_read', 'off') == 'on',
                expires_in_days=int(data['expires_in_days']) if data.get('expires_in_days') else None
            )
            flash('API key created successfully!', 'success')
            return render_template(
                'api_keys/created.html',
                customer=customer,
                api_key=api_key,
                plaintext_key=plaintext
            )
        except Exception as e:
            flash(f'Error creating API key: {str(e)}', 'danger')

    return render_template('api_keys/create.html', customer=customer)


@api_bp.route('/api-keys/<int:key_id>/revoke', methods=['POST'])
@login_required
@admin_required
def revoke_api_key(key_id):
    """Revoke an API key"""
    api_key = ApiKeyService.get_api_key_by_id(key_id)
    if not api_key:
        flash('API key not found', 'danger')
        return redirect(url_for('api.dashboard'))

    if ApiKeyService.revoke_api_key(key_id):
        flash('API key revoked successfully', 'success')
    else:
        flash('Error revoking API key', 'danger')

    return redirect(url_for('api.view_customer', customer_id=api_key.customer_id))


@api_bp.route('/api-keys/<int:key_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_api_key(key_id):
    """Delete an API key permanently"""
    api_key = ApiKeyService.get_api_key_by_id(key_id)
    if not api_key:
        flash('API key not found', 'danger')
        return redirect(url_for('api.dashboard'))

    customer_id = api_key.customer_id

    if ApiKeyService.delete_api_key(key_id):
        flash('API key deleted successfully', 'success')
    else:
        flash('Error deleting API key', 'danger')

    return redirect(url_for('api.view_customer', customer_id=customer_id))


# REST API Endpoints (for programmatic access)

@api_bp.route('/api/v1/customers', methods=['GET'])
@login_required
def api_list_customers():
    """REST API: List all customers"""
    customers = CustomerService.get_all_customers()
    return jsonify([c.to_dict() for c in customers])


@api_bp.route('/api/v1/customers/<int:customer_id>', methods=['GET'])
@login_required
def api_get_customer(customer_id):
    """REST API: Get customer details"""
    customer = CustomerService.get_customer_by_id(customer_id)
    if not customer:
        return jsonify({'error': 'Customer not found'}), 404
    return jsonify(customer.to_dict(include_keys=True))


@api_bp.route('/api/v1/customers/<int:customer_id>/keys', methods=['GET'])
@login_required
def api_list_keys(customer_id):
    """REST API: List API keys for a customer"""
    keys = ApiKeyService.get_customer_keys(customer_id)
    return jsonify([k.to_dict() for k in keys])


# User Management Routes

@api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """List all users"""
    users = UserService.get_all_users()
    return render_template('users/list.html', users=users)


@api_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        data = request.form
        try:
            user = UserService.create_user(
                username=data['username'],
                email=data.get('email'),
                display_name=data.get('display_name'),
                is_admin=data.get('is_admin', 'off') == 'on',
                is_active=data.get('is_active', 'on') == 'on'
            )
            flash(f'User {user.username} created successfully!', 'success')
            return redirect(url_for('api.view_user', user_id=user.id))
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'danger')

    return render_template('users/create.html')


@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def view_user(user_id):
    """View user details"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('api.list_users'))

    return render_template('users/view.html', user=user)


@api_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user details"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('api.list_users'))

    # Prevent editing own admin status
    if user.id == current_user.id and request.method == 'POST':
        is_admin = request.form.get('is_admin', 'off') == 'on'
        if not is_admin and user.is_admin:
            flash('You cannot remove your own admin privileges', 'danger')
            return redirect(url_for('api.edit_user', user_id=user_id))

    if request.method == 'POST':
        data = request.form
        try:
            UserService.update_user(
                user_id,
                email=data.get('email'),
                display_name=data.get('display_name'),
                is_active=data.get('is_active', 'off') == 'on',
                is_admin=data.get('is_admin', 'off') == 'on'
            )
            flash(f'User {user.username} updated successfully!', 'success')
            return redirect(url_for('api.view_user', user_id=user_id))
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'danger')

    return render_template('users/edit.html', user=user)


@api_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_user_admin(user_id):
    """Toggle admin status for a user"""
    if user_id == current_user.id:
        flash('You cannot change your own admin status', 'danger')
        return redirect(url_for('api.view_user', user_id=user_id))

    user = UserService.toggle_admin(user_id)
    if user:
        status = 'granted' if user.is_admin else 'revoked'
        flash(f'Admin privileges {status} for {user.username}', 'success')
    else:
        flash('Error updating user', 'danger')

    return redirect(url_for('api.view_user', user_id=user_id))


@api_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle active status for a user"""
    if user_id == current_user.id:
        flash('You cannot deactivate your own account', 'danger')
        return redirect(url_for('api.view_user', user_id=user_id))

    user = UserService.toggle_active(user_id)
    if user:
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {user.username} {status}', 'success')
    else:
        flash('Error updating user', 'danger')

    return redirect(url_for('api.view_user', user_id=user_id))


@api_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user permanently"""
    if user_id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('api.list_users'))

    user = UserService.get_user_by_id(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('api.list_users'))

    username = user.username

    if UserService.delete_user(user_id):
        flash(f'User {username} deleted successfully', 'success')
    else:
        flash('Error deleting user', 'danger')

    return redirect(url_for('api.list_users'))
