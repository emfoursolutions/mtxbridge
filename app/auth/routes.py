# ABOUTME: Authentication routes for LDAP/AD login and session management
# ABOUTME: Handles user login, logout, and profile using custom LDAP service

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm
from app import db
from app.models.user import User
from app.services.ldap_service import LDAPService


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """LDAP login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('api.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Authenticate against LDAP
        ldap_user = LDAPService.authenticate(username, password)

        if ldap_user:
            # Get or create user in our database
            user = User.query.filter_by(username=username).first()

            if not user:
                # Create new user from LDAP data
                user = User(
                    username=username,
                    email=ldap_user.get('email'),
                    display_name=ldap_user.get('display_name'),
                    dn=ldap_user.get('dn'),
                )
                db.session.add(user)
                db.session.commit()

            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))

            # Update last login
            user.update_last_login()

            # Log the user in
            login_user(user, remember=form.remember_me.data)

            flash(f'Welcome back, {user.display_name or user.username}!', 'success')

            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('api.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout current user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('auth/profile.html', user=current_user)
