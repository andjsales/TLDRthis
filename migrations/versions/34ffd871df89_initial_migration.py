"""Initial migration.

Revision ID: 34ffd871df89
Revises: 
Create Date: 2023-11-15 00:43:44.945177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '34ffd871df89'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('summaries', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('summaries', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###
