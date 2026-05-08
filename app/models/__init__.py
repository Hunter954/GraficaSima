from app import db
from datetime import datetime

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Admin(db.Model, TimestampMixin):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, default='Administrador')
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class Category(db.Model, TimestampMixin):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    show_on_home = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    products = db.relationship('Product', back_populates='category', lazy=True)

class Product(db.Model, TimestampMixin):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    short_description = db.Column(db.String(300))
    full_description = db.Column(db.Text)
    main_image = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    whatsapp_message = db.Column(db.String(400))
    seo_title = db.Column(db.String(180))
    seo_description = db.Column(db.String(300))
    sku = db.Column(db.String(80), index=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    promotional_price = db.Column(db.Numeric(10, 2), nullable=True)
    stock = db.Column(db.Integer, default=0)
    allow_online_purchase = db.Column(db.Boolean, default=False, nullable=False)

    category = db.relationship('Category', back_populates='products')
    images = db.relationship('ProductImage', back_populates='product', cascade='all, delete-orphan', order_by='ProductImage.display_order')
    options = db.relationship('ProductOption', back_populates='product', cascade='all, delete-orphan', order_by='ProductOption.display_order')

class ProductImage(db.Model, TimestampMixin):
    __tablename__ = 'product_images'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    image = db.Column(db.String(255), nullable=False)
    alt_text = db.Column(db.String(180))
    display_order = db.Column(db.Integer, default=0, nullable=False)
    product = db.relationship('Product', back_populates='images')

class ProductOption(db.Model, TimestampMixin):
    __tablename__ = 'product_options'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    value = db.Column(db.String(300), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    product = db.relationship('Product', back_populates='options')


class HomeBanner(db.Model, TimestampMixin):
    __tablename__ = 'home_banners'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180))
    subtitle = db.Column(db.String(260))
    image = db.Column(db.String(255), nullable=False)
    image_mobile = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    link_label = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

class SiteSetting(db.Model, TimestampMixin):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(160), nullable=False, default='Gráfica Azul')
    logo = db.Column(db.String(255))
    favicon = db.Column(db.String(255))
    hero_image = db.Column(db.String(255))
    about_image_1 = db.Column(db.String(255))
    about_image_2 = db.Column(db.String(255))
    about_image_3 = db.Column(db.String(255))
    whatsapp = db.Column(db.String(30))
    email = db.Column(db.String(180))
    phone = db.Column(db.String(60))
    address = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    opening_hours = db.Column(db.String(160))
    seo_title = db.Column(db.String(180))
    seo_description = db.Column(db.String(300))

class Page(db.Model, TimestampMixin):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(180), unique=True, nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    content = db.Column(db.Text, nullable=False)
    seo_title = db.Column(db.String(180))
    seo_description = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

class ContactLead(db.Model, TimestampMixin):
    __tablename__ = 'contact_leads'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140), nullable=False)
    email = db.Column(db.String(180))
    phone = db.Column(db.String(60))
    message = db.Column(db.Text, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product = db.relationship('Product')
