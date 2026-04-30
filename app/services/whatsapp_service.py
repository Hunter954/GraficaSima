from urllib.parse import quote
from flask import current_app, url_for
from app.services.settings_service import get_settings


def product_whatsapp_url(product):
    settings = get_settings()
    phone = ''.join(ch for ch in (settings.whatsapp or '') if ch.isdigit())
    page_url = current_app.config['SITE_URL'] + url_for('public.product_detail', slug=product.slug)
    base_message = product.whatsapp_message or f'Olá! Gostaria de solicitar um orçamento para {product.name}.'
    message = f'{base_message}\nProduto: {product.name}\nLink: {page_url}'
    return f'https://wa.me/{phone}?text={quote(message)}' if phone else '#'


def generic_whatsapp_url(message='Olá! Gostaria de solicitar um orçamento.'):
    settings = get_settings()
    phone = ''.join(ch for ch in (settings.whatsapp or '') if ch.isdigit())
    return f'https://wa.me/{phone}?text={quote(message)}' if phone else '#'
