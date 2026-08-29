"""Initial schema with users, rules, inspections, products, violations, reports, audit_logs

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-25 21:20:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='inspector'),
        sa.Column('badge_number', sa.String(length=100), unique=True, nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('jurisdiction_district', sa.String(length=100), nullable=True),
        sa.Column('jurisdiction_state', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_role', 'users', ['role'])

    # Rule Versions
    op.create_table(
        'rule_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('version_tag', sa.String(length=50), nullable=False, unique=True),
        sa.Column('statutory_act', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('gazette_notification_ref', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
    )

    # Rules
    op.create_table(
        'rules',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('version_id', sa.String(length=36), sa.ForeignKey('rule_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_code', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('statutory_source', sa.String(length=255), nullable=False),
        sa.Column('statutory_penalty_source', sa.String(length=255), nullable=False),
        sa.Column('penalty_first_offence', sa.String(length=100), nullable=True),
        sa.Column('penalty_repeat_offence', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('field_to_validate', sa.String(length=100), nullable=False),
        sa.Column('is_mandatory', sa.Boolean(), server_default='true'),
        sa.Column('validation_type', sa.String(length=50), nullable=False, server_default='presence_and_format'),
        sa.Column('validation_parameters', sa.JSON(), nullable=True),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='critical'),
        sa.Column('state_override', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_rules_code', 'rules', ['rule_code'])
    op.create_index('idx_rules_field', 'rules', ['field_to_validate'])

    # Inspections
    op.create_table(
        'inspections',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('inspection_number', sa.String(length=100), unique=True, nullable=False),
        sa.Column('inspector_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('rule_version_id', sa.String(length=36), sa.ForeignKey('rule_versions.id', ondelete='SET NULL'), nullable=True),
        sa.Column('store_name', sa.String(length=255), nullable=True),
        sa.Column('store_address', sa.Text(), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('gps_latitude', sa.Float(), nullable=True),
        sa.Column('gps_longitude', sa.Float(), nullable=True),
        sa.Column('gps_accuracy_meters', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('compliance_status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('raw_images', sa.JSON(), nullable=True),
        sa.Column('preprocessed_images', sa.JSON(), nullable=True),
        sa.Column('record_sha256_hash', sa.String(length=64), nullable=True),
        sa.Column('qr_verification_token', sa.String(length=255), unique=True, nullable=True),
        sa.Column('is_offline_synced', sa.Boolean(), server_default='false'),
        sa.Column('synced_at', sa.DateTime(), nullable=True),
        sa.Column('inspector_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_inspections_district', 'inspections', ['district'])
    op.create_index('idx_inspections_status', 'inspections', ['compliance_status'])

    # Products
    op.create_table(
        'products',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('inspection_id', sa.String(length=36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('product_name', sa.String(length=255), nullable=True),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('commodity_generic_name', sa.String(length=255), nullable=True),
        sa.Column('mrp_raw', sa.String(length=100), nullable=True),
        sa.Column('mrp_value', sa.Float(), nullable=True),
        sa.Column('mrp_currency', sa.String(length=10), server_default='INR'),
        sa.Column('mrp_inclusive_taxes_declared', sa.Boolean(), nullable=True),
        sa.Column('net_quantity_raw', sa.String(length=100), nullable=True),
        sa.Column('net_quantity_value', sa.Float(), nullable=True),
        sa.Column('net_quantity_unit', sa.String(length=50), nullable=True),
        sa.Column('unit_sale_price_raw', sa.String(length=100), nullable=True),
        sa.Column('batch_number', sa.String(length=100), nullable=True),
        sa.Column('mfg_date_raw', sa.String(length=100), nullable=True),
        sa.Column('mfg_date', sa.Date(), nullable=True),
        sa.Column('exp_date_raw', sa.String(length=100), nullable=True),
        sa.Column('exp_date', sa.Date(), nullable=True),
        sa.Column('manufacturer_name', sa.Text(), nullable=True),
        sa.Column('manufacturer_address', sa.Text(), nullable=True),
        sa.Column('packer_name', sa.Text(), nullable=True),
        sa.Column('packer_address', sa.Text(), nullable=True),
        sa.Column('importer_name', sa.Text(), nullable=True),
        sa.Column('importer_address', sa.Text(), nullable=True),
        sa.Column('country_of_origin', sa.String(length=100), nullable=True),
        sa.Column('consumer_care_email', sa.String(length=255), nullable=True),
        sa.Column('consumer_care_phone', sa.String(length=50), nullable=True),
        sa.Column('consumer_care_address', sa.Text(), nullable=True),
        sa.Column('paddle_raw_text', sa.Text(), nullable=True),
        sa.Column('tesseract_raw_text', sa.Text(), nullable=True),
        sa.Column('extracted_fields_consensus', sa.JSON(), nullable=True),
        sa.Column('has_ocr_disagreement', sa.Boolean(), server_default='false'),
        sa.Column('manual_review_required', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_products_brand', 'products', ['brand_name'])

    # Violations
    op.create_table(
        'violations',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('inspection_id', sa.String(length=36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rule_id', sa.String(length=36), sa.ForeignKey('rules.id', ondelete='SET NULL'), nullable=True),
        sa.Column('rule_code', sa.String(length=100), nullable=False),
        sa.Column('field_affected', sa.String(length=100), nullable=False),
        sa.Column('section_violated', sa.String(length=255), nullable=False),
        sa.Column('statute_title', sa.String(length=255), nullable=False),
        sa.Column('penalty_provision', sa.String(length=255), nullable=False),
        sa.Column('estimated_fine', sa.String(length=100), nullable=True),
        sa.Column('violation_title', sa.String(length=255), nullable=False),
        sa.Column('violation_description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, server_default='critical'),
        sa.Column('is_repeat_offender_alert', sa.Boolean(), server_default='false'),
        sa.Column('evidence_crop_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    # Reports
    op.create_table(
        'reports',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('inspection_id', sa.String(length=36), sa.ForeignKey('inspections.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('docket_number', sa.String(length=100), unique=True, nullable=False),
        sa.Column('pdf_file_path', sa.Text(), nullable=False),
        sa.Column('pdf_download_url', sa.Text(), nullable=True),
        sa.Column('qr_code_image_path', sa.Text(), nullable=True),
        sa.Column('chain_of_custody_hash', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=50), server_default='issued'),
        sa.Column('notice_issued_to', sa.String(length=255), nullable=True),
        sa.Column('serving_date', sa.Date(), nullable=True),
        sa.Column('generated_at', sa.DateTime(), nullable=True),
        sa.Column('signed_by_inspector', sa.Boolean(), server_default='true'),
        sa.Column('inspector_signature_meta', sa.JSON(), nullable=True),
    )

    # Audit Logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('user_id', sa.String(length=36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_name', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('idx_audit_action', 'audit_logs', ['action'])


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('reports')
    op.drop_table('violations')
    op.drop_table('products')
    op.drop_table('inspections')
    op.drop_table('rules')
    op.drop_table('rule_versions')
    op.drop_table('users')
