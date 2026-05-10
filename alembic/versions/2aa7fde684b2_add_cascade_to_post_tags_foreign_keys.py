"""add cascade to post_tags foreign keys

Revision ID: 2aa7fde684b2
Revises: 80927a116872
Create Date: 2026-03-16 03:21:04.816136

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '2aa7fde684b2'
down_revision: Union[str, Sequence[str], None] = '80927a116872'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop existing FK constraints
    op.drop_constraint('post_tags_post_id_fkey', 'post_tags', type_='foreignkey')
    op.drop_constraint('post_tags_tag_id_fkey', 'post_tags', type_='foreignkey')

    # Recreate with CASCADE
    op.create_foreign_key(
        'post_tags_post_id_fkey',
        'post_tags', 'posts',
        ['post_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'post_tags_tag_id_fkey',
        'post_tags', 'tags',
        ['tag_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    # Drop CASCADE constraints
    op.drop_constraint('post_tags_post_id_fkey', 'post_tags', type_='foreignkey')
    op.drop_constraint('post_tags_tag_id_fkey', 'post_tags', type_='foreignkey')

    # Recreate without CASCADE
    op.create_foreign_key(
        'post_tags_post_id_fkey',
        'post_tags', 'posts',
        ['post_id'], ['id']
    )
    op.create_foreign_key(
        'post_tags_tag_id_fkey',
        'post_tags', 'tags',
        ['tag_id'], ['id']
    )
