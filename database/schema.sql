-- Legal Metrology Compliance Scanner
-- Smart India Hackathon 2026
-- Database Schema for PostgreSQL

-- Create Custom Enum Types (Optional if supported, standard VARCHAR with checks used for universal compatibility)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'inspector', -- 'admin', 'inspector', 'supervisor'
    badge_number VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20),
    jurisdiction_district VARCHAR(100),
    jurisdiction_state VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_district ON users(jurisdiction_district);

-- 2. RULES & RULE VERSIONS TABLES (Statute-Grounded & Versioned)
CREATE TABLE IF NOT EXISTS rule_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_tag VARCHAR(50) NOT NULL UNIQUE, -- e.g. "LM-PCR-2011-V2.1-2024"
    statutory_act VARCHAR(255) NOT NULL DEFAULT 'Legal Metrology Act, 2009 & Packaged Commodities Rules, 2011',
    description TEXT,
    gazette_notification_ref VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    published_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_id UUID NOT NULL REFERENCES rule_versions(id) ON DELETE CASCADE,
    rule_code VARCHAR(100) NOT NULL, -- e.g. 'LM_RULE_6_MRP', 'LM_RULE_6_NET_QTY', 'LM_RULE_6_MFG_DATE'
    title VARCHAR(255) NOT NULL,
    statutory_source VARCHAR(255) NOT NULL, -- e.g. 'Rule 6(1)(e), Legal Metrology (Packaged Commodities) Rules, 2011'
    statutory_penalty_source VARCHAR(255) NOT NULL DEFAULT 'Section 36, Legal Metrology Act, 2009',
    penalty_first_offence VARCHAR(100) DEFAULT 'Fine up to ₹25,000',
    penalty_repeat_offence VARCHAR(255) DEFAULT 'Fine up to ₹50,000 or imprisonment up to 1 year',
    description TEXT NOT NULL,
    field_to_validate VARCHAR(100) NOT NULL, -- 'mrp', 'net_quantity', 'batch_no', 'mfg_date', 'exp_date', 'manufacturer', 'country_of_origin', 'consumer_care', 'unit_sale_price'
    is_mandatory BOOLEAN DEFAULT TRUE,
    validation_type VARCHAR(50) NOT NULL DEFAULT 'presence_and_format', -- 'presence_and_format', 'regex', 'unit_check', 'numeric_range', 'date_validity'
    validation_parameters JSONB DEFAULT '{}'::jsonb, -- regex pattern, valid units, required keywords
    severity VARCHAR(50) NOT NULL DEFAULT 'critical', -- 'critical', 'major', 'minor'
    state_override VARCHAR(100), -- NULL for Pan-India rule, or State Name (e.g. 'Maharashtra')
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rules_version ON rules(version_id);
CREATE INDEX IF NOT EXISTS idx_rules_field ON rules(field_to_validate);
CREATE INDEX IF NOT EXISTS idx_rules_code ON rules(rule_code);

-- 3. INSPECTIONS TABLE
CREATE TABLE IF NOT EXISTS inspections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_number VARCHAR(100) UNIQUE NOT NULL, -- e.g. "INSP-MH-MUM-2026-000123"
    inspector_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    rule_version_id UUID REFERENCES rule_versions(id) ON DELETE SET NULL,
    
    -- Location & Premises Context
    store_name VARCHAR(255),
    store_address TEXT,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    gps_latitude NUMERIC(10, 7),
    gps_longitude NUMERIC(10, 7),
    gps_accuracy_meters NUMERIC(6, 2),
    
    -- Inspection Status & Workflow
    status VARCHAR(50) NOT NULL DEFAULT 'completed', -- 'draft', 'preprocessed', 'extracted', 'validated', 'completed', 'disputed'
    compliance_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'compliant', 'non_compliant', 'review_required'
    
    -- Images (Multi-side 360 capture paths/URLs)
    raw_images JSONB DEFAULT '[]'::jsonb, -- [{"side": "front", "url": "..."}, {"side": "back", "url": "..."}, ...]
    preprocessed_images JSONB DEFAULT '[]'::jsonb,
    
    -- Chain of Custody & Immutability
    record_sha256_hash VARCHAR(64), -- SHA-256 hash of core inspection data
    qr_verification_token VARCHAR(255) UNIQUE, -- Public token for instant verification
    is_offline_synced BOOLEAN DEFAULT FALSE,
    synced_at TIMESTAMP WITH TIME ZONE,
    inspector_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_inspections_number ON inspections(inspection_number);
CREATE INDEX IF NOT EXISTS idx_inspections_inspector ON inspections(inspector_id);
CREATE INDEX IF NOT EXISTS idx_inspections_district ON inspections(district);
CREATE INDEX IF NOT EXISTS idx_inspections_status ON inspections(compliance_status);
CREATE INDEX IF NOT EXISTS idx_inspections_created_at ON inspections(created_at);

-- 4. PRODUCTS TABLE (Extracted Entities & Metadata)
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_id UUID NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    product_name VARCHAR(255),
    brand_name VARCHAR(255),
    category VARCHAR(100),
    commodity_generic_name VARCHAR(255),
    
    -- Extracted Declarations (Canonical structured format)
    mrp_raw VARCHAR(100),
    mrp_value NUMERIC(10, 2),
    mrp_currency VARCHAR(10) DEFAULT 'INR',
    mrp_inclusive_taxes_declared BOOLEAN,
    
    net_quantity_raw VARCHAR(100),
    net_quantity_value NUMERIC(10, 3),
    net_quantity_unit VARCHAR(50),
    unit_sale_price_raw VARCHAR(100),
    
    batch_number VARCHAR(100),
    mfg_date_raw VARCHAR(100),
    mfg_date DATE,
    exp_date_raw VARCHAR(100),
    exp_date DATE,
    
    manufacturer_name TEXT,
    manufacturer_address TEXT,
    packer_name TEXT,
    packer_address TEXT,
    importer_name TEXT,
    importer_address TEXT,
    country_of_origin VARCHAR(100),
    
    consumer_care_email VARCHAR(255),
    consumer_care_phone VARCHAR(50),
    consumer_care_address TEXT,
    
    -- OCR Consensus & Confidence Metrics
    paddle_raw_text TEXT,
    tesseract_raw_text TEXT,
    extracted_fields_consensus JSONB DEFAULT '{}'::jsonb, -- per-field consensus scores & engine flags
    has_ocr_disagreement BOOLEAN DEFAULT FALSE,
    manual_review_required BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_inspection ON products(inspection_id);
CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand_name);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON products(manufacturer_name);
CREATE INDEX IF NOT EXISTS idx_products_batch ON products(batch_number);

-- 5. VIOLATIONS TABLE (Specific statutory infractions)
CREATE TABLE IF NOT EXISTS violations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_id UUID NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES rules(id) ON DELETE SET NULL,
    rule_code VARCHAR(100) NOT NULL,
    field_affected VARCHAR(100) NOT NULL,
    
    -- Grounded Statutory Citations
    section_violated VARCHAR(255) NOT NULL, -- e.g. "Rule 6(1)(e) r/w Section 18"
    statute_title VARCHAR(255) NOT NULL, -- "Legal Metrology (Packaged Commodities) Rules, 2011"
    penalty_provision VARCHAR(255) NOT NULL, -- "Section 36, Legal Metrology Act, 2009"
    estimated_fine VARCHAR(100), -- "₹25,000 (First Offence)"
    
    violation_title VARCHAR(255) NOT NULL,
    violation_description TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL DEFAULT 'critical', -- 'critical', 'major', 'minor'
    is_repeat_offender_alert BOOLEAN DEFAULT FALSE,
    evidence_crop_url TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_violations_inspection ON violations(inspection_id);
CREATE INDEX IF NOT EXISTS idx_violations_rule_code ON violations(rule_code);
CREATE INDEX IF NOT EXISTS idx_violations_severity ON violations(severity);

-- 6. REPORTS TABLE (Generated Official Violation Dockets & PDFs)
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inspection_id UUID NOT NULL REFERENCES inspections(id) ON DELETE CASCADE,
    docket_number VARCHAR(100) UNIQUE NOT NULL, -- e.g. "DOCKET-MH-2026-0045"
    pdf_file_path TEXT NOT NULL,
    pdf_download_url TEXT,
    qr_code_image_path TEXT,
    chain_of_custody_hash VARCHAR(64) NOT NULL,
    
    status VARCHAR(50) DEFAULT 'issued', -- 'draft', 'issued', 'signed', 'served', 'archived'
    notice_issued_to VARCHAR(255),
    serving_date DATE,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    signed_by_inspector BOOLEAN DEFAULT TRUE,
    inspector_signature_meta JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_reports_inspection ON reports(inspection_id);
CREATE INDEX IF NOT EXISTS idx_reports_docket ON reports(docket_number);

-- 7. AUDIT LOGS TABLE (Full System Audit Trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL, -- e.g. "USER_LOGIN", "INSPECTION_CREATED", "RULE_UPDATED", "DOCKET_EXPORTED"
    entity_name VARCHAR(100) NOT NULL,
    entity_id VARCHAR(100),
    ip_address VARCHAR(50),
    user_agent TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
