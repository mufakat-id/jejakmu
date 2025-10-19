"""add_site_frontend

Revision ID: 2687ecf43507
Revises: b2cba298c5a3
Create Date: 2025-10-19 07:40:48.745512

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '2687ecf43507'
down_revision = 'b2cba298c5a3'
branch_labels = None
depends_on = None


def upgrade():
    # Add frontend_domain column to site table
    op.add_column('site', sa.Column('frontend_domain', sa.String(length=255), nullable=True))

    # Update existing records with default frontend_domain based on backend domain
    # For localhost:8000 -> localhost:5173
    op.execute("""
        UPDATE site
        SET frontend_domain = 'localhost:5173'
        WHERE domain = 'localhost:8000' AND frontend_domain IS NULL
    """)

    # For other domains, set frontend_domain same as domain (can be updated later via API)
    op.execute("""
        UPDATE site
        SET frontend_domain = domain
        WHERE frontend_domain IS NULL
    """)

    # Make frontend_domain non-nullable after setting values
    op.alter_column('site', 'frontend_domain', nullable=False)


def downgrade():
    # Remove frontend_domain column
    op.drop_column('site', 'frontend_domain')
