"""Create users table

Revision ID: 53972bff8e8c
Revises: 
Create Date: 2020-05-27 20:15:04.416512

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53972bff8e8c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("user",
                    sa.Column("id",sa.Integer,primary_key= True),
                    sa.Column("username",sa.String),
                    sa.Column("password",sa.String))


def downgrade():
    op.drop_table("user")
    
