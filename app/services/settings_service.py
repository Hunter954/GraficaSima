from app.models import SiteSetting


def get_settings():
    settings = SiteSetting.query.first()
    if settings:
        return settings
    return SiteSetting(site_name='Gráfica Azul', whatsapp='5516999999999', email='contato@grafica.com.br')
