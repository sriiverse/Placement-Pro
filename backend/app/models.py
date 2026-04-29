from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ─── Auth User Model ──────────────────────────────────────────────────────────
class AuthUser(db.Model):
    """Stores login credentials. Separate from the placement profile (User)."""
    __tablename__ = 'auth_users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


# ─── Placement Profile Model ──────────────────────────────────────────────────
class User(db.Model):
    """Placement profile — linked 1-to-1 with AuthUser via auth_user_id."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    # Link this profile to an authenticated user account
    auth_user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'), nullable=True, index=True)
    full_name = db.Column(db.String(100), nullable=False)
    target_designation = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    grad_year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.Text, nullable=False)  # CSV string
    internships_count = db.Column(db.Integer, default=0)
    projects_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'full_name': self.full_name,
            'target_designation': self.target_designation,
            'cgpa': self.cgpa,
            'grad_year': self.grad_year,
            'branch': self.branch,
            'skills': self.skills.split(',') if self.skills else [],
            'internships_count': self.internships_count,
            'projects_count': self.projects_count,
            'created_at': self.created_at.isoformat()
        }
