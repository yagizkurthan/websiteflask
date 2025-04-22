from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_mail import Message
from flask_login import login_required, current_user
from .models import User
from . import db, mail
from werkzeug.security import generate_password_hash

views = Blueprint('views', __name__)

# Home Route (for logged-in users)
@views.route('/home', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)

# Contact Route (for the contact form)
@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if name and email and message:
            # Send email using Flask-Mail
            msg = Message(
                subject=f"Contact Form Submission from {name}",
                sender=email,
                recipients=['your-receiving-email@example.com'],  # Replace with your email
                body=f"Name: {name}\nEmail: {email}\nMessage: {message}"
            )
            mail.send(msg)
            flash('Thank you for contacting us! Your message has been sent.', 'success')
        else:
            flash('All fields are required. Please try again.', 'danger')

        return redirect(url_for('views.contact'))

    return render_template("contact.html", user=current_user)

# About Us Route
@views.route('/about')
def about():
    return render_template("about.html", user=current_user)

# Home Route (for visitors or logged-in users)
@views.route("/home1")
def home1():
    user = getattr(current_user, "_get_current_object", lambda: None)() or {"is_authenticated": False}
    return render_template("index.html", user=user)

# Panel Route
@views.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            user_id = request.form.get('id')
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'Security Personnel')  # Default role

            if user_id and name and email and password:
                hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                new_user = User(
                    id=user_id,
                    first_name=name,
                    email=email,
                    password=hashed_password,
                    role=role,
                    is_admin=(role == 'Security Chief')  # Set admin status based on role
                )
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash('User added successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding user: {e}', 'danger')
            else:
                flash('All fields (ID, Name, Email, Password, Role) are required.', 'danger')

        elif action == 'edit':
            user_id = request.form.get('user_id')
            name = request.form.get('name')
            email = request.form.get('email')
            role = request.form.get('role')  # Capture role
            user = User.query.get(user_id)

            if user:
                user.first_name = name
                user.email = email
                user.role = role  # Update role
                user.is_admin = (role == 'Security Chief')  # Update admin status based on role
                db.session.commit()
                flash('User updated successfully!', 'success')
            else:
                flash('User not found.', 'danger')

        elif action == 'delete':
            user_id = request.form.get('user_id')
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully!', 'success')
            else:
                flash('User not found.', 'danger')

    users = User.query.all()
    return render_template("panel.html", user=current_user, users=users)

# Partners Route
@views.route('/partners', methods=['GET'])
def partners():
    hospitals = [
        {"name": "St. Mary's Hospital", "location": "London, UK", "description": "Providing top-tier medical care since 1857."},
        {"name": "Global Health Clinic", "location": "Sydney, Australia", "description": "Innovative health solutions."},
        {"name": "MedLife Center", "location": "New York City, USA", "description": "Advanced medical research and patient care."},
        {"name": "Healing Hands Institute", "location": "Mumbai, India", "description": "Leading healthcare services."},
        {"name": "CarePlus Hospital", "location": "Cape Town, South Africa", "description": "Comprehensive healthcare solutions."},
    ]
    return render_template("partners.html", hospitals=hospitals, user=current_user)
