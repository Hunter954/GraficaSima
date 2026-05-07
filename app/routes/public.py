import bleach
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from app import db
from app.models import Category, Product, Page, ContactLead, HomeBanner
from app.forms import ContactForm
from app.services.whatsapp_service import product_whatsapp_url, generic_whatsapp_url

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    featured = Product.query.filter_by(is_active=True, is_featured=True).order_by(Product.display_order, Product.created_at.desc()).limit(8).all()
    categories = Category.query.filter_by(is_active=True, show_on_home=True).order_by(Category.display_order, Category.name).limit(6).all()
    latest = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).limit(6).all()
    home_banners = HomeBanner.query.filter_by(is_active=True).order_by(HomeBanner.display_order, HomeBanner.created_at.desc()).all()
    return render_template('public/home.html', featured=featured, categories=categories, latest=latest, home_banners=home_banners, whatsapp_url=generic_whatsapp_url())

@public_bp.route('/catalogo')
def catalog():
    q = (request.args.get('q') or '').strip()
    category_slug = request.args.get('categoria') or ''
    order = request.args.get('ordem') or 'destaque'
    page = request.args.get('page', 1, type=int)

    query = Product.query.filter_by(is_active=True).join(Category)
    if q:
        like = f'%{q}%'
        query = query.filter(or_(Product.name.ilike(like), Product.short_description.ilike(like), Product.full_description.ilike(like)))
    current_category = None
    if category_slug:
        current_category = Category.query.filter_by(slug=category_slug, is_active=True).first()
        if current_category:
            query = query.filter(Product.category_id == current_category.id)
    if order == 'az':
        query = query.order_by(Product.name.asc())
    elif order == 'recentes':
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.is_featured.desc(), Product.display_order.asc(), Product.created_at.desc())

    pagination = query.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.filter_by(is_active=True).order_by(Category.display_order, Category.name).all()
    return render_template('public/catalog.html', pagination=pagination, categories=categories, current_category=current_category, q=q, order=order)

@public_bp.route('/produto/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_active=True).first_or_404()
    related = Product.query.filter(Product.id != product.id, Product.category_id == product.category_id, Product.is_active == True).limit(4).all()
    return render_template('public/product_detail.html', product=product, related=related, whatsapp_url=product_whatsapp_url(product), title=product.seo_title, description=product.seo_description)

@public_bp.route('/pagina/<slug>')
def page(slug):
    page_obj = Page.query.filter_by(slug=slug, is_active=True).first_or_404()
    return render_template('public/page.html', page_obj=page_obj, title=page_obj.seo_title or page_obj.title, description=page_obj.seo_description)

@public_bp.route('/contato', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        lead = ContactLead(
            name=bleach.clean(form.name.data), email=bleach.clean(form.email.data or ''),
            phone=bleach.clean(form.phone.data or ''), message=bleach.clean(form.message.data)
        )
        db.session.add(lead)
        db.session.commit()
        flash('Mensagem recebida! Também estamos disponíveis pelo WhatsApp.', 'success')
        return redirect(url_for('public.contact'))
    return render_template('public/contact.html', form=form, whatsapp_url=generic_whatsapp_url())
