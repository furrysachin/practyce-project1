# ER Diagram Explanation – Retail Banking Transaction Analytics

## Entity Relationship Overview

```
                    +──────────+
                    | batches  |
                    +──────────+
                    | batch_id (PK)
                    | file_name
                    | uploaded_at
                    +────┬─────+
                         |
         +───────────────┼───────────────+
         │               │               │
         ▼               ▼               ▼
  +─────────────+  +─────────────+  +───────────+
  |transactions |  |  metadata   |  | (batch_id)|
  +─────────────+  +─────────────+  +───────────+
         │
    +────┴────┐
    │         │
    ▼         ▼
+─────────+  +──────────+
| accounts|  | merchants|
+─────────+  +──────────+
    │
    ▼
+──────────+
| customers|
+──────────+
    │
    ▼
+──────────+
| balances |
+──────────+
```

## Tables and Relationships

### 1. **batches**
- **Role:** Tracks each uploaded JSON file.
- **PK:** `batch_id` (SERIAL).
- **Relationships:** One-to-many to `transactions`, `metadata`.
- **Notes:** `file_name` unique to avoid duplicate file loads.

### 2. **customers**
- **Role:** Customer master (from `account_information.customer_id`, holder name, email, phone).
- **PK:** `customer_id` (from JSON, e.g. `CIF36486679`).
- **Relationships:** One-to-many to `accounts`.

### 3. **accounts**
- **Role:** Bank accounts; one per `account_number`.
- **PK:** `account_id` (SERIAL).
- **FK:** `customer_id` → `customers(customer_id)`.
- **Relationships:** One-to-many to `transactions`, one-to-one to `balances`.

### 4. **merchants**
- **Role:** Merchant master (from `channel_information`: merchant_id, name, category, location).
- **PK:** `merchant_id` (from JSON).
- **Relationships:** One-to-many to `transactions`.

### 5. **transactions**
- **Role:** Fact table; one row per transaction.
- **PK:** `transaction_id` (from JSON).
- **FKs:** `batch_id` → `batches`, `account_id` → `accounts`, `merchant_id` → `merchants`.
- **Unique:** `(reference_number, batch_id)` to support duplicate prevention.

### 6. **balances**
- **Role:** Latest balance snapshot per account.
- **PK:** `balance_id`.
- **FK:** `account_id` → `accounts` (UNIQUE so one row per account).

### 7. **metadata**
- **Role:** Batch-level metadata (e.g. date_range, total_records).
- **PK:** `metadata_id`.
- **FK:** `batch_id` → `batches`.
- **Unique:** `(batch_id, meta_key)`.

## Normalization (1NF, 2NF, 3NF)

- **1NF:** All attributes are atomic; no repeating groups or nested arrays in tables.
- **2NF:** All non-key attributes depend on the whole primary key; no partial dependencies.
- **3NF:** No transitive dependencies; e.g. customer attributes live in `customers`, not in `transactions`.

## One-to-Many / Many-to-One

| From          | To            | Cardinality |
|---------------|---------------|-------------|
| batches       | transactions  | 1:N         |
| batches       | metadata      | 1:N         |
| customers     | accounts      | 1:N         |
| accounts      | transactions  | 1:N         |
| accounts      | balances      | 1:1         |
| merchants     | transactions  | 1:N         |

## JSON to Table Mapping (High Level)

| JSON Path                          | Table(s)     |
|------------------------------------|-------------|
| `batch`, `total_records`, `date_range`, file name | batches, metadata |
| `account_information.customer_id`, holder, email, phone | customers |
| `account_information` (account_number, type, status, …) | accounts |
| `channel_information.merchant_*`, location         | merchants |
| `transaction_identification`, `transaction_details`, `amount_and_currency`, `transaction_status` | transactions |
| `balance_information` (closing/available)         | balances (latest per account) |
