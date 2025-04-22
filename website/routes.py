from flask import Blueprint, render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db

# Define the Blueprint
panel_routes = Blueprint('panel_routes', __name__)

# Route to render the panel page with all users
@panel_routes.route('/panel', methods=['GET', 'POST'])
@login_required
def panel():
    # Check if the current user is an admin
    if not current_user.is_admin:
        flash("Access denied. Admins only.", category="danger")
        return redirect(url_for('views.home'))

    try:
        if request.method == 'POST':
            # Handle form submission based on the action
            action = request.form.get('action')
            
            if action == 'add':
                user_id = request.form.get('user_id')
                first_name = request.form.get('first_name')
                email = request.form.get('email')
                password = request.form.get('password')
                role = request.form.get('role', 'Security Personnel')  # Default to Security Personnel

                # Validate inputs
                if not user_id or not first_name or not email or not password:
                    flash("All fields are required!", category="error")
                elif User.query.filter_by(id=user_id).first():
                    flash("User ID already exists!", category="error")
                elif User.query.filter_by(email=email).first():
                    flash("Email already exists!", category="error")
                else:
                    # Add the new user to the database
                    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
                    new_user = User(
                        id=user_id, 
                        first_name=first_name, 
                        email=email, 
                        password=hashed_password,
                        role=role,
                        is_admin=(role == 'Security Chief')  # Set admin based on role
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    flash("User added successfully!", category="success")
                    return redirect(url_for('panel_routes.panel'))

            elif action == 'edit':
                user_id = request.form.get('user_id')
                first_name = request.form.get('first_name')
                email = request.form.get('email')
                role = request.form.get('role')  # Capture role input
                user = User.query.get(user_id)

                if user:
                    user.first_name = first_name
                    user.email = email
                    user.role = role  # Update the role
                    user.is_admin = (role == 'Security Chief')  # Update admin status based on role
                    db.session.commit()
                    flash("User updated successfully!", category="success")
                else:
                    flash("User not found!", category="error")

            elif action == 'delete':
                user_id = request.form.get('user_id')
                user = User.query.get(user_id)

                if user:
                    db.session.delete(user)
                    db.session.commit()
                    flash("User deleted successfully!", category="success")
                else:
                    flash("User not found!", category="error")

        # Fetch all users from the database
        users = User.query.all()
        return render_template('panel.html', users=users)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error fetching or adding users: {e}")
        flash("An error occurred while processing user data. Please try again later.", category="error")
        return render_template('panel.html', users=[])

views = Blueprint('views', __name__)

@views.route('/partners')
def partners():
    # Example data to be displayed dynamically in the partners.html template
    partners = [
        {"name": "Google Sheets", "description": "Export to spreadsheet in one click"},
        {"name": "Plotly", "description": "Create data viz from any extracted data"},
        {"name": "Excel Spreadsheets", "description": "Create data viz from any extracted data"},
        {"name": "Silk", "description": "Create data viz from any extracted data"},
    ]
    return render_template('partners.html', partners=partners)