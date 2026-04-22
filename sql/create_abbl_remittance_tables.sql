-- Form C / remittance tables for PostgreSQL (schema abbl)
-- Matches app/dbmodels/formc.py — run as a superuser or abbl owner, e.g.:
--   psql -h HOST -U postgres -d Email_App -f sql/create_abbl_remittance_tables.sql

CREATE SCHEMA IF NOT EXISTS abbl;

-- Purpose lookup (dropdown). id = 0 is used by the app for non-ICT flows.
CREATE TABLE IF NOT EXISTS abbl.remittance_purpose (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

INSERT INTO abbl.remittance_purpose (id, name) VALUES
    (0, 'Other / specify in form (non-ICT)'),
    (1, 'Education'),
    (2, 'Family maintenance'),
    (3, 'Medical'),
    (4, 'Savings / investment'),
    (5, 'Travel'),
    (6, 'Goods purchase')
ON CONFLICT (id) DO NOTHING;

-- Main Form C table (IDs are BIGINT timestamp-style from the application)
CREATE TABLE IF NOT EXISTS abbl.remittance (
    id                      BIGINT PRIMARY KEY,
    remitter_name           VARCHAR(255) NOT NULL,
    remitter_address        TEXT NOT NULL,
    remittance_amount       DOUBLE PRECISION NOT NULL,
    remittance_currency     VARCHAR(4) NOT NULL,
    remitted_bank_name      VARCHAR(255) NOT NULL,
    remitted_bank_address   TEXT NOT NULL,
    purpose_of_remittance_id INTEGER NOT NULL,
    applicant_name          VARCHAR(255) NOT NULL,
    applicant_nationality   VARCHAR(50) NOT NULL,
    applicant_address       TEXT NOT NULL,
    application_date        TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    print_date              TIMESTAMP WITHOUT TIME ZONE NULL,
    print_status            INTEGER NOT NULL,
    printed_by              INTEGER NULL,
    remittance_type         VARCHAR(10) NULL,
    "ictPurposeSpecify"     TEXT NOT NULL,
    applicant_mobile        VARCHAR(50) NULL,
    remittance_amount_words TEXT NULL,
    remittance_reference    TEXT NULL,
    CONSTRAINT fk_remittance_purpose
        FOREIGN KEY (purpose_of_remittance_id)
        REFERENCES abbl.remittance_purpose (id)
);

CREATE INDEX IF NOT EXISTS ix_remittance_application_date
    ON abbl.remittance (application_date DESC);

CREATE INDEX IF NOT EXISTS ix_remittance_purpose_id
    ON abbl.remittance (purpose_of_remittance_id);

COMMENT ON TABLE abbl.remittance IS 'Form C (remittance) applications';
COMMENT ON TABLE abbl.remittance_purpose IS 'Lookup for purpose_of_remittance_id';
