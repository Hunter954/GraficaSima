"""add favicon to site settings

Revision ID: 0005_add_favicon_to_site_settings
Revises: 0004_add_show_on_home_to_categories
Create Date: 2026-04-30
"""
from alembic import op
import sqlalchemy as sa

revision = '0005_add_favicon_to_site_settings'
down_revision = '0004_add_show_on_home_to_categories'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('site_settings') as batch_op:
        batch_op.add_column(sa.Column('favicon', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('site_settings') as batch_op:
        batch_op.drop_column('favicon')
