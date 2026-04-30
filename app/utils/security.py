import os
from functools import wraps
from flask import session, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from PIL import Image
import secrets

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'gif'}


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('admin_id'):
            flash('Faça login para acessar o painel.', 'warning')
            return redirect(url_for('admin.login'))
        return fn(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file_storage, subfolder):
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        raise ValueError('Extensão de imagem inválida.')

    original = secure_filename(file_storage.filename)
    ext = original.rsplit('.', 1)[1].lower()
    filename = f"{secrets.token_hex(12)}.{ext}"
    folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    file_storage.save(path)
    try:
        with Image.open(path) as img:
            img.verify()
    except Exception as exc:
        try:
            os.remove(path)
        except OSError:
            pass
        raise ValueError('Arquivo enviado não é uma imagem válida.') from exc
    return f"uploads/{subfolder}/{filename}"
