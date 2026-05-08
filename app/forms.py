from flask_wtf import FlaskForm
from flask_wtf.file import FileField, MultipleFileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, IntegerField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif']
FAVICON_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp', 'gif', 'ico']

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=180)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6, max=120)])
    submit = SubmitField('Entrar')


class AdminUserForm(FlaskForm):
    name = StringField('Nome do administrador', validators=[DataRequired(), Length(max=120)])
    email = StringField('E-mail de acesso', validators=[DataRequired(), Email(), Length(max=180)])
    password = PasswordField('Senha', validators=[Optional(), Length(min=6, max=120)], description='Preencha somente se quiser definir ou trocar a senha.')
    confirm_password = PasswordField('Confirmar senha', validators=[Optional(), EqualTo('password', message='As senhas precisam ser iguais.')])
    is_active = BooleanField('Administrador ativo')
    submit = SubmitField('Salvar administrador')

class CategoryForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=140)])
    slug = StringField('Slug', validators=[Optional(), Length(max=180)])
    description = TextAreaField('Descrição', validators=[Optional(), Length(max=2000)])
    image = FileField('Icone/imagem da categoria', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    is_active = BooleanField('Ativa')
    show_on_home = BooleanField('Exibir nos destaques da home')
    display_order = IntegerField('Ordem', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Salvar')

class ProductForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=180)])
    slug = StringField('Slug', validators=[Optional(), Length(max=220)])
    category_id = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    short_description = TextAreaField('Descrição curta', validators=[Optional(), Length(max=300)])
    full_description = TextAreaField('Descrição completa', validators=[Optional()])
    main_image = FileField('Imagem principal', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    gallery = MultipleFileField('Galeria', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    is_active = BooleanField('Ativo')
    is_featured = BooleanField('Produto em destaque')
    display_order = IntegerField('Ordem', validators=[Optional(), NumberRange(min=0)], default=0)
    options_text = TextAreaField('Opções disponíveis', validators=[Optional()], description='Uma opção por linha no formato Nome: Valor')
    whatsapp_message = TextAreaField('Mensagem personalizada WhatsApp', validators=[Optional(), Length(max=400)])
    seo_title = StringField('SEO title', validators=[Optional(), Length(max=180)])
    seo_description = TextAreaField('SEO description', validators=[Optional(), Length(max=300)])
    sku = StringField('SKU', validators=[Optional(), Length(max=80)])
    price = DecimalField('Preço futuro', validators=[Optional()], places=2)
    promotional_price = DecimalField('Preço promocional futuro', validators=[Optional()], places=2)
    stock = IntegerField('Estoque futuro', validators=[Optional()], default=0)
    allow_online_purchase = BooleanField('Permitir compra online no futuro')
    submit = SubmitField('Salvar')


class HomeBannerForm(FlaskForm):
    title = StringField('Título do banner', validators=[Optional(), Length(max=180)])
    subtitle = TextAreaField('Texto curto', validators=[Optional(), Length(max=260)])
    image = FileField('Imagem desktop do banner 1140x340', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    image_mobile = FileField('Imagem mobile do banner 720x420', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    link_url = StringField('Link do banner', validators=[Optional(), Length(max=255)])
    link_label = StringField('Texto do botão', validators=[Optional(), Length(max=80)])
    is_active = BooleanField('Ativo')
    display_order = IntegerField('Ordem', validators=[Optional(), NumberRange(min=0)], default=0)
    submit = SubmitField('Salvar')

class SettingsForm(FlaskForm):
    site_name = StringField('Nome da gráfica', validators=[DataRequired(), Length(max=160)])
    logo = FileField('Logo', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    favicon = FileField('Favicon do site', validators=[Optional(), FileAllowed(FAVICON_EXTENSIONS, 'Apenas imagens ou .ico')])
    hero_image = FileField('Imagem do destaque inicial', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    about_image_1 = FileField('Imagem Nossa historia - card 1', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    about_image_2 = FileField('Imagem Nossa historia - card 2', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    about_image_3 = FileField('Imagem Nossa historia - card 3', validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, 'Apenas imagens')])
    whatsapp = StringField('WhatsApp', validators=[Optional(), Length(max=30)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=180)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=60)])
    address = StringField('Endereço', validators=[Optional(), Length(max=255)])
    instagram = StringField('URL do Instagram', validators=[Optional(), Length(max=255)])
    facebook = StringField('URL do Facebook', validators=[Optional(), Length(max=255)])
    linkedin = StringField('LinkedIn', validators=[Optional(), Length(max=255)])
    opening_hours = StringField('Horário de atendimento', validators=[Optional(), Length(max=160)])
    seo_title = StringField('SEO title', validators=[Optional(), Length(max=180)])
    seo_description = TextAreaField('SEO description', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Salvar')

class ContactForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired(), Length(max=140)])
    email = StringField('E-mail', validators=[Optional(), Email(), Length(max=180)])
    phone = StringField('Telefone', validators=[Optional(), Length(max=60)])
    message = TextAreaField('Mensagem', validators=[DataRequired(), Length(max=3000)])
    submit = SubmitField('Enviar')
