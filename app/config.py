import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or f"sqlite:///{BASE_DIR / 'instance' / 'dev.db'}"
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 5 * 1024 * 1024))

    # Pasta real de uploads.
    # Em deploy com volume persistente montado em /data, salvamos no volume
    # e o app cria um link publico em app/static/uploads para as URLs existentes.
    _upload_env = os.getenv('UPLOAD_FOLDER')
    _persistent_upload_env = os.getenv('PERSISTENT_UPLOAD_FOLDER')
    if _persistent_upload_env:
        UPLOAD_FOLDER = _persistent_upload_env
    elif os.path.isdir('/data'):
        UPLOAD_FOLDER = '/data'
    elif _upload_env:
        UPLOAD_FOLDER = str((BASE_DIR / _upload_env).resolve()) if not os.path.isabs(_upload_env) else _upload_env
    else:
        UPLOAD_FOLDER = str(BASE_DIR / 'app' / 'static' / 'uploads')

    SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:5000').rstrip('/')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_HTTPONLY = True
    WTF_CSRF_TIME_LIMIT = None
