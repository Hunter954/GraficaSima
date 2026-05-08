"""add mobile image to home banners

Revision ID: 0007_add_mobile_image_to_home_banners
Revises: 0006_add_home_banners
Create Date: 2026-05-08
"""
from alembic import op
import sqlalchemy as sa

revision = '0007_add_mobile_image_to_home_banners'
down_revision = '0006_add_home_banners'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('home_banners', sa.Column('image_mobile', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('home_banners', 'image_mobile')
