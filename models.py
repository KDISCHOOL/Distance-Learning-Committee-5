from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Faculty(db.Model):
    __tablename__ = "faculties"
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, nullable=True)  # 뷰용 순번
    korean_name = db.Column(db.String(200), unique=True, index=True, nullable=False)
    english_name = db.Column(db.String(200))
    category = db.Column(db.String(50))  # 전임/비전임
    email = db.Column(db.String(254))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CourseModality(db.Model):
    __tablename__ = "course_modalities"
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Integer, nullable=True)  # 뷰용 순번
    name = db.Column(db.String(200), index=True, nullable=False)  # Instructor name (Korean or English combined)
    year = db.Column(db.Integer)
    semester = db.Column(db.String(50))
    language = db.Column(db.String(50))
    course_title = db.Column(db.String(500))
    time_slot = db.Column(db.String(100))
    day = db.Column(db.String(50))
    time = db.Column(db.String(50))
    frequency_week = db.Column(db.String(50))
    course_format = db.Column(db.String(200))
    apply_flag = db.Column(db.Boolean, default=False)  # Apply this semester (Yes/No)
    apply_reason = db.Column(db.Text)  # Reason for Applying (unicode up to 1000 chars)
    modified_date = db.Column(db.DateTime)  # stored as UTC datetime
    password_hash = db.Column(db.String(128))  # hashed 4-digit PIN (if provided per-row)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_pin(self, pin_plain: str):
        if not pin_plain:
            self.password_hash = None
            return
        self.password_hash = generate_password_hash(pin_plain)

    def check_pin(self, pin_plain: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, pin_plain)
