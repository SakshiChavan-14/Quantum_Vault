"""add_pqc_crypto_and_audit_logs

Revision ID: c123456789ab
Revises: b123456789ab
Create Date: 2026-08-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c123456789ab'
down_revision: Union[str, Sequence[str], None] = 'b123456789ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to include Post-Quantum Cryptography metadata and Audit Logs."""
    
    # 1. Add Post-Quantum Kyber-1024 key columns to users table
    op.add_column('users', sa.Column('kyber_public_key', sa.Text(), nullable=True, comment='User Kyber-1024 public key in hex'))
    op.add_column('users', sa.Column('kyber_secret_key_encrypted', sa.Text(), nullable=True, comment='User Kyber-1024 secret key encrypted with master key'))

    # 2. Add PQC Version 2 metadata columns to files table
    op.add_column('files', sa.Column('kyber_ciphertext', sa.Text(), nullable=True, comment='Kyber-1024 KEM ciphertext (hex string)'))
    op.add_column('files', sa.Column('encrypted_dek', sa.Text(), nullable=True, comment='AES-256 DEK wrapped with HKDF KEK (hex string)'))
    op.add_column('files', sa.Column('encryption_nonce', sa.String(length=64), nullable=True, comment='AES-256-GCM 96-bit nonce (hex)'))

    # 3. Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False, comment='Unique audit log identifier'),
        sa.Column('user_id', sa.String(length=36), nullable=True, comment='User who triggered event'),
        sa.Column('file_id', sa.String(length=36), nullable=True, comment='Target file identifier'),
        sa.Column('event_type', sa.String(length=100), nullable=False, comment='Specific event name'),
        sa.Column('event_category', sa.String(length=50), nullable=False, comment='Category: AUTH, FILE, CRYPTO, SECURITY, SYSTEM'),
        sa.Column('status', sa.String(length=20), nullable=False, comment='Status: SUCCESS, FAILURE, WARNING, INFO'),
        sa.Column('message', sa.Text(), nullable=False, comment='Human-readable event summary'),
        sa.Column('metadata_json', sa.Text(), nullable=True, comment='Sanitized JSON metadata'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='Client IP address'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='SET NULL'),
    )

    # 4. Create indexes for audit_logs table
    op.create_index('idx_audit_user_id', 'audit_logs', ['user_id'], unique=False)
    op.create_index('idx_audit_file_id', 'audit_logs', ['file_id'], unique=False)
    op.create_index('idx_audit_event_type', 'audit_logs', ['event_type'], unique=False)
    op.create_index('idx_audit_event_category', 'audit_logs', ['event_category'], unique=False)
    op.create_index('idx_audit_status', 'audit_logs', ['status'], unique=False)
    op.create_index('idx_audit_created_at', 'audit_logs', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_audit_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_status', table_name='audit_logs')
    op.drop_index('idx_audit_event_category', table_name='audit_logs')
    op.drop_index('idx_audit_event_type', table_name='audit_logs')
    op.drop_index('idx_audit_file_id', table_name='audit_logs')
    op.drop_index('idx_audit_user_id', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_column('files', 'encryption_nonce')
    op.drop_column('files', 'encrypted_dek')
    op.drop_column('files', 'kyber_ciphertext')

    op.drop_column('users', 'kyber_secret_key_encrypted')
    op.drop_column('users', 'kyber_public_key')
