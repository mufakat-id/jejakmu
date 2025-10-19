"""add_sites_table

Revision ID: b2cba298c5a3
Revises: 960e89eae168
Create Date: 2025-10-19 07:15:14.083177

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision = 'b2cba298c5a3'
down_revision = '960e89eae168'
branch_labels = None
depends_on = None


def upgrade():
    # Create site table
    op.create_table(
        'site',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_site_domain'), 'site', ['domain'], unique=True)
    op.create_index(op.f('ix_site_is_default'), 'site', ['is_default'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_site_is_default'), table_name='site')
    op.drop_index(op.f('ix_site_domain'), table_name='site')

    # Drop table
    op.drop_table('site')
