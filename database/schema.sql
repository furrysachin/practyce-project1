-- =============================================================================
-- Retail Banking Transaction Analytics - PostgreSQL Schema
-- Normalized design: 1NF, 2NF, 3NF
-- =============================================================================

-- Drop existing objects (for clean install)
DROP TABLE IF EXISTS balances CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;
DROP TABLE IF EXISTS metadata CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TABLE IF EXISTS merchants CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS batches CASCADE;

-- =============================================================================
-- BATCHES - One row per uploaded JSON file
-- =============================================================================
CREATE TABLE batches (
    batch_id       SERIAL PRIMARY KEY,
    file_name      VARCHAR(512) NOT NULL,
    source_batch   VARCHAR(64),           -- original "batch" string from JSON (e.g. BATCH_007)
    total_records  INTEGER DEFAULT 0,
    date_from      DATE,
    date_to        DATE,
    generated_at   TIMESTAMPTZ,
    uploaded_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (file_name)
);

CREATE INDEX idx_batches_uploaded_at ON batches(uploaded_at);
CREATE INDEX idx_batches_source_batch ON batches(source_batch);

-- =============================================================================
-- CUSTOMERS - Master data (deduplicated by customer_id from JSON)
-- =============================================================================
CREATE TABLE customers (
    customer_id     VARCHAR(32) PRIMARY KEY,
    name            VARCHAR(256) NOT NULL,
    email           VARCHAR(256),
    phone           VARCHAR(32),
    pan_number      VARCHAR(32),
    customer_segment VARCHAR(64),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_segment ON customers(customer_segment);

-- =============================================================================
-- ACCOUNTS - One per account_number, linked to customer
-- =============================================================================
CREATE TABLE accounts (
    account_id        SERIAL PRIMARY KEY,
    customer_id       VARCHAR(32) NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    account_number    VARCHAR(64) NOT NULL,
    account_type      VARCHAR(64),
    status            VARCHAR(32),
    branch_code       VARCHAR(32),
    iban              VARCHAR(64),
    swift_code        VARCHAR(32),
    sort_code         VARCHAR(32),
    account_open_date DATE,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (account_number)
);

CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_type ON accounts(account_type);

-- =============================================================================
-- MERCHANTS - Master data (deduplicated by merchant_id)
-- =============================================================================
CREATE TABLE merchants (
    merchant_id   VARCHAR(32) PRIMARY KEY,
    merchant_name VARCHAR(256) NOT NULL,
    category      VARCHAR(32),            -- merchant_category_code
    location      VARCHAR(128),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_merchants_category ON merchants(category);
CREATE INDEX idx_merchants_name ON merchants(merchant_name);

-- =============================================================================
-- TRANSACTIONS - Fact table, one row per transaction
-- =============================================================================
CREATE TABLE transactions (
    transaction_id     VARCHAR(64) PRIMARY KEY,
    batch_id           INTEGER NOT NULL REFERENCES batches(batch_id) ON DELETE RESTRICT,
    account_id         INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
    merchant_id        VARCHAR(32) REFERENCES merchants(merchant_id) ON DELETE SET NULL,
    reference_number   VARCHAR(64),
    transaction_date   DATE NOT NULL,
    transaction_datetime TIMESTAMPTZ,
    transaction_type   VARCHAR(64),
    transaction_category VARCHAR(128),
    transaction_code   VARCHAR(32),
    currency_code      VARCHAR(8) DEFAULT 'INR',
    transaction_amount NUMERIC(18, 2) NOT NULL,
    net_amount         NUMERIC(18, 2),
    status             VARCHAR(32),
    status_code        VARCHAR(16),
    payment_network    VARCHAR(32),
    channel_type       VARCHAR(64),
    created_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_transactions_batch ON transactions(batch_id);
CREATE INDEX idx_transactions_account ON transactions(account_id);
CREATE INDEX idx_transactions_merchant ON transactions(merchant_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE UNIQUE INDEX idx_transactions_ref_batch ON transactions(reference_number, batch_id);

-- =============================================================================
-- BALANCES - Latest balance snapshot per account (updated on ingestion)
-- =============================================================================
CREATE TABLE balances (
    balance_id         SERIAL PRIMARY KEY,
    account_id         INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
    current_balance    NUMERIC(18, 2),
    available_balance  NUMERIC(18, 2),
    ledger_balance     NUMERIC(18, 2),
    as_of_transaction_id VARCHAR(64),    -- last tx that produced this balance
    updated_at         TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (account_id)
);

CREATE INDEX idx_balances_account ON balances(account_id);

-- =============================================================================
-- METADATA - Batch-level metadata (key-value or structured)
-- =============================================================================
CREATE TABLE metadata (
    metadata_id   SERIAL PRIMARY KEY,
    batch_id      INTEGER NOT NULL REFERENCES batches(batch_id) ON DELETE CASCADE,
    meta_key      VARCHAR(128) NOT NULL,
    meta_value    TEXT,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metadata_batch ON metadata(batch_id);
CREATE UNIQUE INDEX idx_metadata_batch_key ON metadata(batch_id, meta_key);

-- =============================================================================
-- COMMENTS
-- =============================================================================
COMMENT ON TABLE batches IS 'One record per uploaded JSON file; tracks file origin';
COMMENT ON TABLE customers IS 'Customer master; from account_information in JSON';
COMMENT ON TABLE accounts IS 'Bank accounts; one-to-many with customers';
COMMENT ON TABLE merchants IS 'Merchant master; from channel_information';
COMMENT ON TABLE transactions IS 'Transaction fact table; links account, merchant, batch';
COMMENT ON TABLE balances IS 'Latest balance per account';
COMMENT ON TABLE metadata IS 'Batch-level metadata (e.g. date_range, total_records)';
