"""Add Article and Topic models

Revision ID: 16f6f1c7e19f
Revises: 61749658ada6
Create Date: [Your Date]

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '16f6f1c7e19f'
down_revision = '61749658ada6'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Skip creating tables if they exist
    if 'topics' not in inspector.get_table_names():
        op.create_table('topics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )

    if 'articles' not in inspector.get_table_names():
        op.create_table('articles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('content_md', sa.Text(), nullable=False),
            sa.Column('content_html', sa.Text(), nullable=True),
            sa.Column('date_published', sa.DateTime(), nullable=True),
            sa.Column('author_id', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    if 'article_topics' not in inspector.get_table_names():
        op.create_table('article_topics',
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('topic_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
            sa.ForeignKeyConstraint(['topic_id'], ['topics.id'], ),
            sa.PrimaryKeyConstraint('article_id', 'topic_id')
        )

    # Add foreign key to users if not already present
    existing_fks = [fk['constrained_columns'][0] for fk in inspector.get_foreign_keys('users')]
    if 'default_currency_code' not in existing_fks:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.create_foreign_key(
                'users_ibfk_1',
                'currency',
                ['default_currency_code'],
                ['code']
            )

def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # Drop foreign key from users if it exists
    existing_fks = [fk['constrained_columns'][0] for fk in inspector.get_foreign_keys('users')]
    if 'default_currency_code' in existing_fks:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.drop_constraint('users_ibfk_1', type_='foreignkey')

    # Drop tables if they exist
    for table in ['article_topics', 'articles', 'topics']:
        if table in inspector.get_table_names():
            op.drop_table(table)