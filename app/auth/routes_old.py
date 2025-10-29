# ABOUTME: Authentication routes for LDAP/AD login and session management
# ABOUTME: Handles user login, logout, and callback from LDAP authentication

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_ldap3_login.forms import LDAPLoginForm

from app.auth import auth_bp
from app import db
from app.models.user import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """LDAP login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('api.dashboard'))

    form = LDAPLoginForm()

    if form.validate_on_submit():
        # LDAP authentication is handled by flask-ldap3-login
        # On successful LDAP auth, we need to get or create the user
        ldap_user = form.user
        if ldap_user:
            user = User.query.filter_by(username=form.username.data).first()

            if not user:
                # Create new user from LDAP data
                user = User(
                    username=form.username.data,
                    email=getattr(ldap_user, 'mail', [None])[0] if hasattr(ldap_user, 'mail') else None,
                    display_name=getattr(ldap_user, 'displayName', [None])[0] if hasattr(ldap_user, 'displayName') else None,
                    dn=ldap_user.dn if hasattr(ldap_user, 'dn') else None,
                )
                db.session.add(user)
                db.session.commit()

            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))

            # Update last login
            user.update_last_login()

            # Log the user in
            login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)

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
