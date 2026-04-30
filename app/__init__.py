import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('app.config.Config')
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'categories'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'site'), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models import Admin, Category, Product, ProductImage, ProductOption, SiteSetting, Page, ContactLead
    ensure_database_compatibility(app)

    from app.routes.public import public_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    register_cli(app)
    register_template_helpers(app)
    return app



def ensure_database_compatibility(app):
    """Ensure small schema additions exist when the app starts on an older database."""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if not inspector.has_table('site_settings'):
                return

            columns = {column['name'] for column in inspector.get_columns('site_settings')}
            if 'hero_image' not in columns:
                with db.engine.begin() as connection:
                    connection.execute(text('ALTER TABLE site_settings ADD COLUMN hero_image VARCHAR(255)'))
        except (OperationalError, ProgrammingError) as exc:
            message = str(exc).lower()
            if 'hero_image' in message and ('duplicate' in message or 'already exists' in message):
                return
            raise

def register_template_helpers(app):
    from app.services.settings_service import get_settings
    from app.services.whatsapp_service import product_whatsapp_url, generic_whatsapp_url
    from app.utils.formatters import money_br

    @app.context_processor
    def inject_global_settings():
        return {
            'site_settings': get_settings(),
            'money_br': money_br,
            'product_whatsapp_url': product_whatsapp_url,
            'generic_whatsapp_url': generic_whatsapp_url,
        }


def register_cli(app):
    import click
    from werkzeug.security import generate_password_hash
    from app.models import Admin, Category, Product, ProductOption, SiteSetting, Page
    from slugify import slugify

    @app.cli.command('seed')
    def seed():
        """Create initial admin, settings, pages, categories and products."""
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@grafica.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        if not Admin.query.filter_by(email=admin_email).first():
            db.session.add(Admin(email=admin_email, password_hash=generate_password_hash(admin_password), name='Administrador'))

        if not SiteSetting.query.first():
            db.session.add(SiteSetting(
                site_name='Gráfica Azul', whatsapp='5516999999999', email='contato@graficaazul.com.br',
                phone='(16) 99999-9999', address='Rua Exemplo, 123 - Centro',
                instagram='https://instagram.com/', facebook='https://facebook.com/', linkedin='',
                opening_hours='Segunda a sexta, 8h às 18h', seo_title='Gráfica Azul - Impressos e Comunicação Visual',
                seo_description='Produtos gráficos, brindes, adesivos, banners e materiais personalizados com atendimento via WhatsApp.'
            ))

        pages = {
            'sobre': ('Sobre a gráfica', 'Somos uma gráfica focada em qualidade, agilidade e atendimento próximo. Produzimos impressos, comunicação visual e materiais personalizados para empresas de todos os portes.'),
            'politica-de-privacidade': ('Política de privacidade', 'Coletamos apenas os dados necessários para contato, orçamento e atendimento. Não vendemos dados pessoais a terceiros.'),
            'termos-de-uso': ('Termos de uso', 'As informações do site são apresentadas para fins comerciais e podem ser alteradas sem aviso prévio.'),
            'orientacoes-de-producao': ('Orientações de produção', 'Envie arquivos em PDF/X-1a, CMYK, 300 DPI, com sangria mínima de 3 mm. A produção inicia após conferência e aprovação da arte.'),
        }
        for slug, (title, content) in pages.items():
            if not Page.query.filter_by(slug=slug).first():
                db.session.add(Page(slug=slug, title=title, content=content, seo_title=title, seo_description=content[:150]))

        categories = ['Adesivos', 'Banners', 'Panfletos', 'Cartões de Visita', 'Brindes', 'Comunicação Visual']
        cat_map = {}
        for idx, name in enumerate(categories, start=1):
            cat = Category.query.filter_by(slug=slugify(name)).first()
            if not cat:
                cat = Category(name=name, slug=slugify(name), description=f'Produtos de {name.lower()} personalizados para sua empresa.', is_active=True, display_order=idx)
                db.session.add(cat)
                db.session.flush()
            cat_map[name] = cat

        products = [
            ('Panfleto 15x21cm', 'Panfletos', 'Impressão frente e verso em papel couchê para campanhas promocionais.', True),
            ('Cartão de Visita Premium', 'Cartões de Visita', 'Cartões com acabamento profissional para fortalecer sua marca.', True),
            ('Adesivo Vinil Recortado', 'Adesivos', 'Adesivos resistentes para vitrines, embalagens, carros e sinalização.', True),
            ('Banner Lona 440g', 'Banners', 'Banner com ótima durabilidade para eventos, lojas e divulgações.', True),
            ('Sacola Personalizada', 'Brindes', 'Sacolas úteis e personalizadas para ações promocionais.', False),
            ('Placa PS Comunicação Visual', 'Comunicação Visual', 'Placas para sinalização interna e externa.', False),
        ]
        for idx, (name, cat_name, short, featured) in enumerate(products, start=1):
            if not Product.query.filter_by(slug=slugify(name)).first():
                p = Product(
                    name=name, slug=slugify(name), category=cat_map[cat_name], short_description=short,
                    full_description=f'{short} Trabalhamos com diferentes formatos, materiais, acabamentos e quantidades. Solicite um orçamento personalizado pelo WhatsApp.',
                    is_active=True, is_featured=featured, display_order=idx,
                    whatsapp_message=f'Olá! Gostaria de solicitar um orçamento para {name}.',
                    seo_title=f'{name} | Gráfica Azul', seo_description=short,
                    sku=f'GRAF-{idx:03}', stock=0, allow_online_purchase=False
                )
                db.session.add(p)
                db.session.flush()
                options = [
                    ('Formatos', 'A6, A5, A4, personalizados'),
                    ('Materiais', 'Couchê, offset, adesivo, lona ou PS conforme produto'),
                    ('Acabamentos', 'Refile, laminação, verniz, ilhós, corte especial'),
                    ('Prazo médio', '3 a 7 dias úteis após aprovação da arte'),
                ]
                for k, v in options:
                    db.session.add(ProductOption(product=p, name=k, value=v))

        db.session.commit()
        click.echo('Seed concluído. Admin: %s' % admin_email)
