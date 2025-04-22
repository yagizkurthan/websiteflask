from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# Index Route
@auth.route('/')
def index():
    return render_template("index.html", user=current_user)

# Login Route
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        password = request.form.get('password')

        # Fetch user by ID
        user = User.query.filter_by(id=user_id).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash('Logged in successfully!', category='success')
            return redirect(url_for('views.home'))
        flash('Invalid User ID or Password.', category='error')

    return render_template("login.html", user=current_user)

# Logout Route
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out.', category='success')
    return redirect(url_for('auth.index'))

# Sign-Up Route
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        first_name = request.form.get('firstName')
        email = request.form.get('email')  # New email input
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Validation checks
        errors = []
        if not user_id or not user_id.isdigit() or len(user_id) != 9:
            errors.append('User ID must be exactly 9 digits.')
        if User.query.filter_by(id=user_id).first():
            errors.append('User ID already exists. Please use another.')
        if User.query.filter_by(email=email).first():
            errors.append('Email already exists. Please use another.')
        if not first_name or len(first_name) < 2:
            errors.append('First name must be greater than 1 character.')
        if not email or '@' not in email:
            errors.append('A valid email is required.')
        if password1 != password2:
            errors.append('Passwords do not match.')
        if not password1 or len(password1) < 7:
            errors.append('Password must be at least 7 characters long.')

        # Display all errors
        if errors:
            for error in errors:
                flash(error, category='error')
        else:
            # Create new user
            new_user = User(
                id=user_id,
                first_name=first_name,
                email=email,  # Include email in user creation
                password=generate_password_hash(password1, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
