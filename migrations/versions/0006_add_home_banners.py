"""add home banners

Revision ID: 0006_add_home_banners
Revises: 0005_add_favicon_to_site_settings
Create Date: 2026-05-07
"""
from alembic import op
import sqlalchemy as sa

revision = '0006_add_home_banners'
down_revision = '0005_add_favicon_to_site_settings'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'home_banners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=180), nullable=True),
        sa.Column('subtitle', sa.String(length=260), nullable=True),
        sa.Column('image', sa.String(length=255), nullable=False),
        sa.Column('link_url', sa.String(length=255), nullable=True),
        sa.Column('link_label', sa.String(length=80), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('home_banners')
