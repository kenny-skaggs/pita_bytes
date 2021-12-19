"""first migration

Revision ID: b8b5aaa9f14a
Revises: 
Create Date: 2021-12-19 12:54:44.865081

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8b5aaa9f14a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ingredients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('steps',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.SmallInteger(), nullable=True),
        sa.Column('description', sa.String(length=2000), nullable=True),
        sa.Column('recipe_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('steps')
    op.drop_table('measurements')
    op.drop_table('recipes')
    op.drop_table('ingredients')
    # ### end Alembic commands ###