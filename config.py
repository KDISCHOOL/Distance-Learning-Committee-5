import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'dlc.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PIN = os.environ.get("ADMIN_PIN", "1205")  # 기본값은 1205 (환경변수로 변경 권장)
    # 기타 설정
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
