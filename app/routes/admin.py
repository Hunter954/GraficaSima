import bleach
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import check_password_hash, generate_password_hash
from slugify import slugify
from app import db
from app.models import Admin, Category, Product, ProductImage, ProductOption, HomeBanner, SiteSetting
from app.forms import LoginForm, AdminUserForm, CategoryForm, ProductForm, HomeBannerForm, SettingsForm
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
        'banners': HomeBanner.query.count(),
        'admins': Admin.query.count(),
        'active_admins': Admin.query.filter_by(is_active=True).count(),
    }
    latest = Product.query.order_by(Product.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html', stats=stats, latest=latest)


@admin_bp.route('/administradores')
@admin_required
def admin_users():
    items = Admin.query.order_by(Admin.is_active.desc(), Admin.name.asc()).all()
    return render_template('admin/admins/list.html', items=items)

@admin_bp.route('/administradores/novo', methods=['GET', 'POST'])
@admin_required
def admin_user_create():
    form = AdminUserForm(is_active=True)
    form.password.validators = [validator for validator in form.password.validators if validator.__class__.__name__ != 'Optional']
    if form.validate_on_submit():
        email = normalize_email(form.email.data)
        if Admin.query.filter_by(email=email).first():
            flash('Já existe um administrador com este e-mail.', 'danger')
            return render_template('admin/admins/form.html', form=form, title='Novo administrador')
        admin = Admin(
            name=bleach.clean(form.name.data),
            email=email,
            password_hash=generate_password_hash(form.password.data),
            is_active=bool(form.is_active.data),
        )
        db.session.add(admin)
        db.session.commit()
        flash('Administrador criado com sucesso.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/admins/form.html', form=form, title='Novo administrador')

@admin_bp.route('/administradores/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_user_edit(id):
    admin = Admin.query.get_or_404(id)
    form = AdminUserForm(obj=admin)
    if form.validate_on_submit():
        email = normalize_email(form.email.data)
        duplicated = Admin.query.filter(Admin.email == email, Admin.id != admin.id).first()
        if duplicated:
            flash('Já existe outro administrador com este e-mail.', 'danger')
            return render_template('admin/admins/form.html', form=form, title='Editar administrador', admin=admin)
        requested_active = bool(form.is_active.data)
        if admin.id == session.get('admin_id') and not requested_active:
            flash('Você não pode desativar o seu próprio usuário enquanto está logado.', 'danger')
            form.is_active.data = True
            return render_template('admin/admins/form.html', form=form, title='Editar administrador', admin=admin)
        if admin.is_active and not requested_active and active_admin_count(excluding_id=admin.id) == 0:
            flash('Mantenha pelo menos um administrador ativo no painel.', 'danger')
            form.is_active.data = True
            return render_template('admin/admins/form.html', form=form, title='Editar administrador', admin=admin)

        admin.name = bleach.clean(form.name.data)
        admin.email = email
        admin.is_active = requested_active
        if form.password.data:
            admin.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        if admin.id == session.get('admin_id'):
            session['admin_name'] = admin.name
        flash('Administrador atualizado com sucesso.', 'success')
        return redirect(url_for('admin.admin_users'))
    return render_template('admin/admins/form.html', form=form, title='Editar administrador', admin=admin)

@admin_bp.route('/administradores/<int:id>/alternar', methods=['POST'])
@admin_required
def admin_user_toggle(id):
    admin = Admin.query.get_or_404(id)
    if admin.id == session.get('admin_id'):
        flash('Você não pode desativar o seu próprio usuário enquanto está logado.', 'danger')
        return redirect(url_for('admin.admin_users'))
    if admin.is_active and active_admin_count(excluding_id=admin.id) == 0:
        flash('Mantenha pelo menos um administrador ativo no painel.', 'danger')
        return redirect(url_for('admin.admin_users'))
    admin.is_active = not admin.is_active
    db.session.commit()
    flash('Status do administrador atualizado.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/administradores/<int:id>/excluir', methods=['POST'])
@admin_required
def admin_user_delete(id):
    admin = Admin.query.get_or_404(id)
    if admin.id == session.get('admin_id'):
        flash('Você não pode excluir o seu próprio usuário enquanto está logado.', 'danger')
        return redirect(url_for('admin.admin_users'))
    if admin.is_active and active_admin_count(excluding_id=admin.id) == 0:
        flash('Mantenha pelo menos um administrador ativo no painel.', 'danger')
        return redirect(url_for('admin.admin_users'))
    db.session.delete(admin)
    db.session.commit()
    flash('Administrador excluído com sucesso.', 'success')
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/categorias')
@admin_required
def categories():
    items = Category.query.order_by(Category.display_order, Category.name).all()
    return render_template('admin/categories/list.html', items=items)

@admin_bp.route('/categorias/nova', methods=['GET', 'POST'])
@admin_required
def category_create():
    form = CategoryForm(is_active=True, show_on_home=True)
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

@admin_bp.route('/produtos/<int:id>/duplicar', methods=['POST'])
@admin_required
def product_duplicate(id):
    original = Product.query.get_or_404(id)
    duplicate = Product(
        category_id=original.category_id,
        name=f'{original.name} - Cópia',
        slug=make_unique_product_slug(f'{original.slug}-copia'),
        short_description=original.short_description,
        full_description=original.full_description,
        main_image=original.main_image,
        is_active=False,
        is_featured=False,
        display_order=original.display_order,
        whatsapp_message=original.whatsapp_message,
        seo_title=original.seo_title,
        seo_description=original.seo_description,
        sku='',
        price=original.price,
        promotional_price=original.promotional_price,
        stock=original.stock,
        allow_online_purchase=original.allow_online_purchase,
    )
    db.session.add(duplicate)
    db.session.flush()

    for image in original.images:
        db.session.add(ProductImage(
            product=duplicate,
            image=image.image,
            alt_text=image.alt_text,
            display_order=image.display_order,
        ))

    for option in original.options:
        db.session.add(ProductOption(
            product=duplicate,
            name=option.name,
            value=option.value,
            display_order=option.display_order,
        ))

    db.session.commit()
    flash('Produto duplicado. Revise e ative a cópia quando estiver pronta.', 'success')
    return redirect(url_for('admin.product_edit', id=duplicate.id))

@admin_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
@admin_required
def product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('Produto excluído.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/banners')
@admin_required
def banners():
    items = HomeBanner.query.order_by(HomeBanner.display_order, HomeBanner.created_at.desc()).all()
    return render_template('admin/banners/list.html', items=items)

@admin_bp.route('/banners/novo', methods=['GET', 'POST'])
@admin_required
def banner_create():
    form = HomeBannerForm(is_active=True)
    if form.validate_on_submit():
        banner = HomeBanner()
        try:
            fill_banner(banner, form, require_image=True)
        except ValueError:
            return render_template('admin/banners/form.html', form=form, title='Novo banner da home')
        db.session.add(banner)
        db.session.commit()
        flash('Banner criado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banners/form.html', form=form, title='Novo banner da home')

@admin_bp.route('/banners/<int:id>/editar', methods=['GET', 'POST'])
@admin_required
def banner_edit(id):
    banner = HomeBanner.query.get_or_404(id)
    form = HomeBannerForm(obj=banner)
    if form.validate_on_submit():
        fill_banner(banner, form, require_image=False)
        db.session.commit()
        flash('Banner atualizado.', 'success')
        return redirect(url_for('admin.banners'))
    return render_template('admin/banners/form.html', form=form, title='Editar banner da home', banner=banner)

@admin_bp.route('/banners/<int:id>/alternar', methods=['POST'])
@admin_required
def banner_toggle(id):
    banner = HomeBanner.query.get_or_404(id)
    banner.is_active = not banner.is_active
    db.session.commit()
    flash('Status do banner atualizado.', 'success')
    return redirect(url_for('admin.banners'))

@admin_bp.route('/banners/<int:id>/excluir', methods=['POST'])
@admin_required
def banner_delete(id):
    banner = HomeBanner.query.get_or_404(id)
    db.session.delete(banner)
    db.session.commit()
    flash('Banner excluído.', 'success')
    return redirect(url_for('admin.banners'))

@admin_bp.route('/configuracoes', methods=['GET', 'POST'])
@admin_required
def settings():
    settings = SiteSetting.query.first() or SiteSetting()
    form = SettingsForm(obj=settings) if request.method == 'GET' else SettingsForm()
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
        if has_uploaded_file(form.logo.data):
            settings.logo = save_image(form.logo.data, 'site')
        if has_uploaded_file(form.favicon.data):
            settings.favicon = save_image(form.favicon.data, 'site')
        if has_uploaded_file(form.hero_image.data):
            settings.hero_image = save_image(form.hero_image.data, 'site')
        if has_uploaded_file(form.about_image_1.data):
            settings.about_image_1 = save_image(form.about_image_1.data, 'site')
        if has_uploaded_file(form.about_image_2.data):
            settings.about_image_2 = save_image(form.about_image_2.data, 'site')
        if has_uploaded_file(form.about_image_3.data):
            settings.about_image_3 = save_image(form.about_image_3.data, 'site')
        db.session.add(settings)
        db.session.commit()
        flash('Configurações salvas.', 'success')
        return redirect(url_for('admin.settings'))
    return render_template('admin/settings.html', form=form, settings=settings)



def normalize_email(value):
    return (value or '').lower().strip()


def active_admin_count(excluding_id=None):
    query = Admin.query.filter_by(is_active=True)
    if excluding_id is not None:
        query = query.filter(Admin.id != excluding_id)
    return query.count()


def fill_banner(banner, form, require_image=False):
    banner.title = bleach.clean(form.title.data or '')
    banner.subtitle = bleach.clean(form.subtitle.data or '')
    banner.link_url = bleach.clean(form.link_url.data or '')
    banner.link_label = bleach.clean(form.link_label.data or '')
    banner.is_active = bool(form.is_active.data)
    banner.display_order = form.display_order.data or 0
    if has_uploaded_file(form.image.data):
        banner.image = save_image(form.image.data, 'banners')
    if has_uploaded_file(form.image_mobile.data):
        banner.image_mobile = save_image(form.image_mobile.data, 'banners')
    elif require_image and not banner.image:
        flash('Envie uma imagem para criar o banner.', 'danger')
        raise ValueError('Imagem obrigatória')

def has_uploaded_file(value):
    return bool(value and hasattr(value, 'filename') and value.filename)


def uploaded_files(value):
    if not value:
        return []
    if not isinstance(value, (list, tuple)):
        value = [value]
    return [item for item in value if has_uploaded_file(item)]


def prepare_product_form(form):
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]


def fill_category(cat, form):
    cat.name = bleach.clean(form.name.data)
    cat.slug = slugify(form.slug.data or form.name.data)
    cat.description = bleach.clean(form.description.data or '')
    cat.is_active = bool(form.is_active.data)
    cat.show_on_home = bool(form.show_on_home.data)
    cat.display_order = form.display_order.data or 0
    if has_uploaded_file(form.image.data):
        cat.image = save_image(form.image.data, 'categories')



def make_unique_product_slug(base_slug):
    base = slugify(base_slug) or 'produto-copia'
    candidate = base
    counter = 2
    while Product.query.filter_by(slug=candidate).first():
        candidate = f'{base}-{counter}'
        counter += 1
    return candidate


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

    if has_uploaded_file(form.main_image.data):
        product.main_image = save_image(form.main_image.data, 'products')

    db.session.flush()
    for idx, img in enumerate(uploaded_files(form.gallery.data), start=1):
        path = save_image(img, 'products')
        db.session.add(ProductImage(product=product, image=path, alt_text=product.name, display_order=idx))

    ProductOption.query.filter_by(product=product).delete()
    lines = (form.options_text.data or '').splitlines()
    for idx, line in enumerate(lines, start=1):
        if ':' in line:
            name, value = line.split(':', 1)
            if name.strip() and value.strip():
                db.session.add(ProductOption(product=product, name=bleach.clean(name.strip()), value=bleach.clean(value.strip()), display_order=idx))
