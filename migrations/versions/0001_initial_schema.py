"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-04-30 15:25:00

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('email', sa.String(length=180), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_admins_email'), 'admins', ['email'], unique=False)

    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('slug', sa.String(length=180), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=False)

    op.create_table(
        'pages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=180), nullable=False),
        sa.Column('title', sa.String(length=180), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('seo_title', sa.String(length=180), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_pages_slug'), 'pages', ['slug'], unique=False)

    op.create_table(
        'site_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('site_name', sa.String(length=160), nullable=False),
        sa.Column('logo', sa.String(length=255), nullable=True),
        sa.Column('whatsapp', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=180), nullable=True),
        sa.Column('phone', sa.String(length=60), nullable=True),
        sa.Column('address', sa.String(length=255), nullable=True),
        sa.Column('instagram', sa.String(length=255), nullable=True),
        sa.Column('facebook', sa.String(length=255), nullable=True),
        sa.Column('linkedin', sa.String(length=255), nullable=True),
        sa.Column('opening_hours', sa.String(length=160), nullable=True),
        sa.Column('seo_title', sa.String(length=180), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=180), nullable=False),
        sa.Column('slug', sa.String(length=220), nullable=False),
        sa.Column('short_description', sa.String(length=300), nullable=True),
        sa.Column('full_description', sa.Text(), nullable=True),
        sa.Column('main_image', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_featured', sa.Boolean(), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('whatsapp_message', sa.String(length=400), nullable=True),
        sa.Column('seo_title', sa.String(length=180), nullable=True),
        sa.Column('seo_description', sa.String(length=300), nullable=True),
        sa.Column('sku', sa.String(length=80), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('promotional_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stock', sa.Integer(), nullable=True),
        sa.Column('allow_online_purchase', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index(op.f('ix_products_slug'), 'products', ['slug'], unique=False)
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=False)

    op.create_table(
        'contact_leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=140), nullable=False),
        sa.Column('email', sa.String(length=180), nullable=True),
        sa.Column('phone', sa.String(length=60), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'product_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('image', sa.String(length=255), nullable=False),
        sa.Column('alt_text', sa.String(length=180), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'product_options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('value', sa.String(length=300), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('product_options')
    op.drop_table('product_images')
    op.drop_table('contact_leads')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_index(op.f('ix_products_slug'), table_name='products')
    op.drop_table('products')
    op.drop_table('site_settings')
    op.drop_index(op.f('ix_pages_slug'), table_name='pages')
    op.drop_table('pages')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_table('categories')
    op.drop_index(op.f('ix_admins_email'), table_name='admins')
    op.drop_table('admins')
