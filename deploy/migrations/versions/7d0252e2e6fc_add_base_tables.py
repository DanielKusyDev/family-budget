"""Add base tables

Revision ID: 7d0252e2e6fc
Revises: 
Create Date: 2022-11-01 16:08:00.567844

"""
import sqlalchemy as sa
from alembic import op

revision = "7d0252e2e6fc"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "budget",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1023), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("password"),
    )
    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(length=1023), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("budget_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["budget_id"], ["budget.id"], name="transaction_budget_fk"),
        sa.ForeignKeyConstraint(["category_id"], ["category.id"], name="transaction_category_fk"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("transaction")
    op.drop_table("user")
    op.drop_table("category")
    op.drop_table("budget")
