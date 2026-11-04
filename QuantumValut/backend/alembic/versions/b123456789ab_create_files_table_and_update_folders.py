"""create_files_table_and_update_folders

Revision ID: b123456789ab
Revises: 3892c70922b8
Create Date: 2026-07-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b123456789ab'
down_revision: Union[str, Sequence[str], None] = '3892c70922b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    # Create files table
    op.create_table('files',
    sa.Column('id', sa.String(length=36), nullable=False, comment='Unique file identifier (UUID)'),
    sa.Column('owner_id', sa.String(length=36), nullable=False, comment='File owner (User ID)'),
    sa.Column('folder_id', sa.String(length=36), nullable=True, comment='Parent folder (Folder ID)'),
    sa.Column('original_filename', sa.String(length=500), nullable=False, comment='Original filename as uploaded by user'),
    sa.Column('stored_filename', sa.String(length=100), nullable=False, comment='Hash-based filename for storage'),
    sa.Column('file_size', sa.BigInteger(), nullable=False, comment='File size in bytes'),
    sa.Column('mime_type', sa.String(length=100), nullable=False, comment='MIME type (e.g., application/pdf)'),
    sa.Column('file_extension', sa.String(length=20), nullable=True, comment='File extension (e.g., pdf, docx, jpg)'),
    sa.Column('storage_path', sa.String(length=1000), nullable=False, comment='Relative path to file in storage'),
    sa.Column('file_hash', sa.String(length=64), nullable=True, comment='SHA-256 hash of original file'),
    sa.Column('is_encrypted', sa.Boolean(), nullable=False, comment='Whether file is encrypted (AES-256)'),
    sa.Column('encryption_algorithm', sa.String(length=50), nullable=True, comment='Encryption algorithm (e.g., AES-256)'),
    sa.Column('encryption_key_hash', sa.String(length=255), nullable=True, comment='Encrypted AES key (Kyber-protected)'),
    sa.Column('description', sa.Text(), nullable=True, comment='User-provided file description'),
    sa.Column('is_favorite', sa.Boolean(), nullable=False, comment='Mark file as favorite'),
    sa.Column('is_shared', sa.Boolean(), nullable=False, comment='Whether file is shared'),
    sa.Column('version', sa.Integer(), nullable=False, comment='File version number'),
    sa.Column('last_modified_by', sa.String(length=36), nullable=True, comment='User who last modified file'),
    sa.Column('last_accessed_at', sa.DateTime(), nullable=True, comment='Last download/access time'),
    sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='Soft delete timestamp'),
    sa.Column('access_count', sa.Integer(), nullable=False, comment='Number of times file has been downloaded/accessed'),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['folder_id'], ['folders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['last_modified_by'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('stored_filename', name='uq_file_stored_filename')
    )
    
    # Create indexes for files table
    op.create_index(op.f('ix_files_owner_id'), 'files', ['owner_id'], unique=False)
    op.create_index(op.f('ix_files_folder_id'), 'files', ['folder_id'], unique=False)
    op.create_index(op.f('ix_files_deleted_at'), 'files', ['deleted_at'], unique=False)
    op.create_index(op.f('ix_files_is_favorite'), 'files', ['is_favorite'], unique=False)
    op.create_index(op.f('ix_files_created_at'), 'files', ['created_at'], unique=False)
    op.create_index(op.f('ix_files_hash'), 'files', ['file_hash'], unique=False)
    op.create_index('idx_file_stored_filename', 'files', ['stored_filename'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    
    # Drop files table indexes
    op.drop_index('idx_file_stored_filename', table_name='files')
    op.drop_index(op.f('ix_files_hash'), table_name='files')
    op.drop_index(op.f('ix_files_created_at'), table_name='files')
    op.drop_index(op.f('ix_files_is_favorite'), table_name='files')
    op.drop_index(op.f('ix_files_deleted_at'), table_name='files')
    op.drop_index(op.f('ix_files_folder_id'), table_name='files')
    op.drop_index(op.f('ix_files_owner_id'), table_name='files')
    
    # Drop files table
    op.drop_table('files')
