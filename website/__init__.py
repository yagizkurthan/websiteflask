from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_migrate import Migrate
from os import path
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{path.abspath(path.dirname(__file__))}/{DB_NAME}"
    app.config['MAIL_SERVER'] = 'smtp.example.com'  # Update with your SMTP server
    app.config['MAIL_PORT'] = 587                  # Update with your mail port
    app.config['MAIL_USE_TLS'] = True              # Update based on your mail server
    app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Update with your email
    app.config['MAIL_PASSWORD'] = 'your-password'  # Update with your email password

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    # Import blueprints
    from .views import views
    from .auth import auth
    from .routes import panel_routes

    # Register blueprints
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(panel_routes, url_prefix='/panel')

    # Import models
    from .models import User

    # Create database and default admin if not exists
    with app.app_context():
        db.create_all()
        create_default_admin()

    # User authentication setup
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_default_admin():
    """Creates a default admin user with a predefined ID and credentials if not already present."""
    from .models import User
    admin_id = 220408011
    admin_email = "ykurthan0@gmail.com"
    admin_password = "1234567"

    admin = User.query.filter_by(id=admin_id).first()
    if not admin:
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        admin = User(
            id=admin_id,
            first_name="Yağız Kurthan",
            email=admin_email,
            password=hashed_password,
            is_admin=True,
            role="Security Chief"  # Default role for admin
        )
        db.session.add(admin)
        db.session.commit()
        print(f"Default admin created with ID {admin_id}.")
