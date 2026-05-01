"""add show_on_home to categories

Revision ID: 0004_add_show_on_home_to_categories
Revises: 0003_add_about_images_to_site_settings
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa

revision = '0004_add_show_on_home_to_categories'
down_revision = '0003_add_about_images_to_site_settings'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('categories') as batch_op:
        batch_op.add_column(sa.Column('show_on_home', sa.Boolean(), nullable=False, server_default=sa.true()))
    with op.batch_alter_table('categories') as batch_op:
        batch_op.alter_column('show_on_home', server_default=None)


def downgrade():
    with op.batch_alter_table('categories') as batch_op:
        batch_op.drop_column('show_on_home')
