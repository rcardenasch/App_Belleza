"""Add duracion_promedio_minutos to disponibilidades

Revision ID: 0002_add_duracion_promedio
Revises: 
Create Date: 2026-06-24 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_duracion_promedio'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Añade la columna con valor por defecto 60 para evitar problemas en tablas existentes
    op.add_column(
        'disponibilidades',
        sa.Column('duracion_promedio_minutos', sa.Integer(), nullable=False, server_default=sa.text('60'))
    )
    # Opcional: eliminar el server_default si prefieres no mantenerlo en el esquema
    op.alter_column('disponibilidades', 'duracion_promedio_minutos', server_default=None)


def downgrade():
    op.drop_column('disponibilidades', 'duracion_promedio_minutos')

