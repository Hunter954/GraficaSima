import bleach
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import check_password_hash
from slugify import slugify
from app import db
from app.models import Admin, Category, Product, ProductImage, ProductOption, SiteSetting
from app.forms import LoginForm, CategoryForm, ProductForm, SettingsForm
from app.utils.security import admin_required, save_image

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data.lower().strip(), is_active=True).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            session.clear()
            session['admin_id'] = admin.id
            session['admin_name'] = admin.name
            flash('Login realizado com sucesso.', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('E-mail ou senha inválidos.', 'danger')
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do painel.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    stats = {
        'total_products': Product.query.count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
        'inactive_products': Product.query.filter_by(is_active=False).count(),
        'categories': Category.query.count(),
        'featured': Product.query.filter_by(is_featured=True).count(),
    }
    latest = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest=latest)

@admin_bp.route('/categorias')
@admin_required
def categories():
    items = Category.query.order_by(Category.display_order, Category.name).all()
    return render_template('admin/categories/list.html', items=items)

@admin_bp.route('/categorias/nova', methods=['GET', 'POST'])
@admin_required
def category_create():
    form = CategoryForm(is_active=True)
    if form.validate_on_submit():
        cat = Category()
        fill_category(cat, form)
        db.session.add(cat)
        db.session.commit()
        flash('Categoria criada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/categories/form.html', form=form, title='Nova categoria')

@admin_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def category_edit(id):
    cat = Category.query.get_or_404(id)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        fill_category(cat, form)
        db.session.commit()
        flash('Categoria atualizada.', 'success')
        return redirect(url_for('admin.categories'))
    return render_template('admin/categories/form.html', form=form, title='Editar categoria')

@admin_bp.route('/categorias/<int:id>/alternar', methods=['POST'])
@admin_required
def category_toggle(id):
    cat = Category.query.get_or_404(id)
    cat.is_active = not cat.is_active
    db.session.commit()
    flash('Status da categoria atualizado.', 'success')
    return redirect(url_for('admin.categories'))

@admin_bp.route('/produtos')
@admin_required
def products():
    items = Product.query.order_by(Product.display_order, Product.created_at.desc()).all()
    return render_template('admin/products/list.html', items=items)

@admin_bp.route('/produtos/novo', methods=['GET', 'POST'])
@admin_required
def product_create():
    form = ProductForm(is_active=True)
    prepare_product_form(form)
    if form.validate_on_submit():
        product = Product()
        fill_product(product, form)
        db.session.add(product)
        db.session.commit()
        flash('Produto criado.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/form.html', form=form, title='Novo produto')

@admin_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def product_edit(id):
    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    prepare_product_form(form)
    if request.method == 'GET':
        form.options_text.data = '\n'.join([f'{o.name}: {o.value}' for o in product.options])
    if form.validate_on_submit():
        fill_product(product, form)
        db.session.commit()
        flash('Produto atualizado.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/products/form.html', form=form, title='Editar produto', product=product)

@admin_bp.route('/produtos/<int:id>/alternar', methods=['POST'])
@admin_required
def product_toggle(id):
    product = Product.query.get_or_404(id)
    product.is_active = not product.is_active
    db.session.commit()
    flash('Status do produto atualizado.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
@admin_required
def product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído.', 'success')
    return redirect(url_for('admin.products'))

@admin_bp.route('/configuracoes', methods=['GET', 'POST'])
@admin_required
def settings():
    settings = SiteSetting.query.first() or SiteSetting()
    form = SettingsForm(obj=settings)
    if form.validate_on_submit():
        settings.site_name = bleach.clean(form.site_name.data)
        settings.whatsapp = bleach.clean(form.whatsapp.data or '')
        settings.email = bleach.clean(form.email.data or '')
        settings.phone = bleach.clean(form.phone.data or '')
        settings.address = bleach.clean(form.address.data or '')
        settings.instagram = bleach.clean(form.instagram.data or '')
        settings.facebook = bleach.clean(form.facebook.data or '')
        settings.linkedin = bleach.clean(form.linkedin.data or '')
        settings.opening_hours = bleach.clean(form.opening_hours.data or '')
        settings.seo_title = bleach.clean(form.seo_title.data or '')
        settings.seo_description = bleach.clean(form.seo_description.data or '')
        if form.logo.data and form.logo.data.filename:
            settings.logo = save_image(form.logo.data, 'site')
        db.session.add(settings)
        db.session.commit()
        flash('Configurações salvas.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', form=form, settings=settings)


def prepare_product_form(form):
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


def fill_category(cat, form):
    cat.name = bleach.clean(form.name.data)
    cat.slug = slugify(form.slug.data or form.name.data)
    cat.description = bleach.clean(form.description.data or '')
    cat.is_active = bool(form.is_active.data)
    cat.display_order = form.display_order.data or 0
    if form.image.data and form.image.data.filename:
        cat.image = save_image(form.image.data, 'categories')


def fill_product(product, form):
    product.name = bleach.clean(form.name.data)
    product.slug = slugify(form.slug.data or form.name.data)
    product.category_id = form.category_id.data
    product.short_description = bleach.clean(form.short_description.data or '')
    product.full_description = bleach.clean(form.full_description.data or '', tags=['p','br','strong','b','em','ul','ol','li','a'], attributes={'a':['href','title','target']})
    product.is_active = bool(form.is_active.data)
    product.is_featured = bool(form.is_featured.data)
    product.display_order = form.display_order.data or 0
    product.whatsapp_message = bleach.clean(form.whatsapp_message.data or '')
    product.seo_title = bleach.clean(form.seo_title.data or '')
    product.seo_description = bleach.clean(form.seo_description.data or '')
    product.sku = bleach.clean(form.sku.data or '')
    product.price = form.price.data
    product.promotional_price = form.promotional_price.data
    product.stock = form.stock.data or 0
    product.allow_online_purchase = bool(form.allow_online_purchase.data)

    if form.main_image.data and form.main_image.data.filename:
        product.main_image = save_image(form.main_image.data, 'products')

    db.session.flush()
    if form.gallery.data:
        for idx, img in enumerate(form.gallery.data, start=1):
            if img and img.filename:
                path = save_image(img, 'products')
                db.session.add(ProductImage(product=product, image=path, alt_text=product.name, display_order=idx))

    ProductOption.query.filter_by(product=product).delete()
    lines = (form.options_text.data or '').splitlines()
    for idx, line in enumerate(lines, start=1):
        if ':' in line:
            name, value = line.split(':', 1)
            if name.strip() and value.strip():
                db.session.add(ProductOption(product=product, name=bleach.clean(name.strip()), value=bleach.clean(value.strip()), display_order=idx))
