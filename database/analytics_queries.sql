-- =============================================================================
-- Retail Banking Transaction Analytics - Optimized SQL Queries
-- =============================================================================

-- 1. Total transactions per batch
SELECT
    b.batch_id,
    b.file_name,
    b.uploaded_at,
    COUNT(t.transaction_id) AS total_transactions
FROM batches b
LEFT JOIN transactions t ON t.batch_id = b.batch_id
GROUP BY b.batch_id, b.file_name, b.uploaded_at
ORDER BY b.uploaded_at DESC;

-- 2. Total transaction amount (overall and per batch)
-- Per batch:
SELECT
    b.batch_id,
    b.file_name,
    COALESCE(SUM(t.transaction_amount), 0) AS total_amount
FROM batches b
LEFT JOIN transactions t ON t.batch_id = b.batch_id
GROUP BY b.batch_id, b.file_name;

-- Overall:
SELECT COALESCE(SUM(transaction_amount), 0) AS total_transaction_volume
FROM transactions;

-- 3. Unique customers (overall and per batch)
-- Per batch:
SELECT
    b.batch_id,
    COUNT(DISTINCT a.customer_id) AS unique_customers
FROM batches b
JOIN transactions t ON t.batch_id = b.batch_id
JOIN accounts a ON a.account_id = t.account_id
GROUP BY b.batch_id;

-- Overall:
SELECT COUNT(DISTINCT a.customer_id) AS unique_customers
FROM transactions t
JOIN accounts a ON a.account_id = t.account_id;

-- 4. Transaction type distribution (per batch and overall)
-- Per batch:
SELECT
    batch_id,
    transaction_type,
    COUNT(*) AS count
FROM transactions
WHERE batch_id = :batch_id
GROUP BY batch_id, transaction_type
ORDER BY count DESC;

-- Overall:
SELECT
    transaction_type,
    COUNT(*) AS count
FROM transactions
GROUP BY transaction_type
ORDER BY count DESC;

-- 5. Top 10 merchants (by transaction count)
SELECT
    m.merchant_id,
    m.merchant_name,
    m.category,
    COUNT(t.transaction_id) AS transaction_count,
    COALESCE(SUM(t.transaction_amount), 0) AS total_amount
FROM merchants m
JOIN transactions t ON t.merchant_id = m.merchant_id
GROUP BY m.merchant_id, m.merchant_name, m.category
ORDER BY transaction_count DESC
LIMIT 10;

-- 6. Account activity frequency (most active accounts)
SELECT
    a.account_id,
    a.account_number,
    a.account_type,
    a.customer_id,
    COUNT(t.transaction_id) AS transaction_count
FROM accounts a
JOIN transactions t ON t.account_id = a.account_id
GROUP BY a.account_id, a.account_number, a.account_type, a.customer_id
ORDER BY transaction_count DESC
LIMIT 20;
