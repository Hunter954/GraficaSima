"""add hero image to site settings

Revision ID: 0002_add_hero_image_to_site_settings
Revises: 0001_initial_schema
Create Date: 2026-04-30 16:20:00

"""
from alembic import op
import sqlalchemy as sa

revision = '0002_add_hero_image_to_site_settings'
down_revision = '0001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('site_settings', sa.Column('hero_image', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('site_settings', 'hero_image')
