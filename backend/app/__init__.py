import os
from flask import Flask
from flask_cors import CORS
from .models import db

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow requests from the React frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Configure Database (SQLite for local development)
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize plugins
    db.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
    # Register blueprints (routes)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "service": "placement-pro-core"}, 200
        
    return app
