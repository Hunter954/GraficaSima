"""add about images to site settings

Revision ID: 0003_add_about_images_to_site_settings
Revises: 0002_add_hero_image_to_site_settings
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_add_about_images_to_site_settings'
down_revision = '0002_add_hero_image_to_site_settings'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_settings') as batch_op:
        batch_op.add_column(sa.Column('about_image_1', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('about_image_2', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('about_image_3', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('site_settings') as batch_op:
        batch_op.drop_column('about_image_3')
        batch_op.drop_column('about_image_2')
        batch_op.drop_column('about_image_1')
