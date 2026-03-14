# Retail Banking Transaction Analytics System

End-to-end system to ingest JSON banking transaction files, normalize them into a PostgreSQL schema, and serve analytics via APIs and a React dashboard.

## Architecture

```
JSON Files → FastAPI Ingestion API → Parser & Transformer → PostgreSQL
                                                                  ↓
React Dashboard ← Summary APIs ← Analytics Query Layer
```

## Tech Stack

| Layer     | Technology        |
|----------|--------------------|
| Backend  | Python, FastAPI    |
| Database | PostgreSQL         |
| ORM      | SQLAlchemy         |
| JSON     | Python `json`      |
| Driver   | psycopg2           |
| Frontend | React.js           |
| Charts   | Recharts           |
| HTTP     | Axios              |

## Project Structure

```
practyc/
├── database/
│   ├── schema.sql           # PostgreSQL DDL (1NF, 2NF, 3NF)
│   └── analytics_queries.sql # Optimized summary queries
├── docs/
│   └── ER_DIAGRAM.md        # Entity relationship explanation
├── backend/
│   ├── main.py              # FastAPI app, CORS, routes
│   ├── config.py            # Settings (DB URL, etc.)
│   ├── database.py          # SQLAlchemy engine & session
│   ├── models/              # SQLAlchemy ORM models
│   ├── routes/              # Upload & summary APIs
│   ├── services/
│   │   ├── json_parser.py  # Normalize nested JSON
│   │   ├── ingestion.py     # Insert with batch tracking
│   │   └── analytics.py     # Summary queries
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/client.js    # Axios API client
│   │   ├── components/      # Dashboard, cards, charts, upload
│   │   ├── App.js
│   │   └── index.js
│   └── package.json
├── retail_banking_transactions_*.json  # Sample data (optional)
└── README.md
```

## Database Setup

1. Create a PostgreSQL database:

```bash
createdb retail_banking
```

2. Set connection string (optional):

```bash
export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/retail_banking"
```

3. Run schema:

```bash
psql -U postgres -d retail_banking -f database/schema.sql
```

Or let the backend create tables on first run (development):

- Backend `main.py` can call `init_db()` so tables are created from SQLAlchemy models. For production, prefer running `schema.sql` and migrations.

## Backend

1. Create virtualenv and install dependencies:

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Unix: source venv/bin/activate
pip install -r requirements.txt
```

2. Run FastAPI:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. APIs:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/upload/json` | Upload JSON file (multipart `file`) |
| GET    | `/api/summary/file/{batch_id}` | File-level summary |
| GET    | `/api/summary/overall` | Overall analytics |
| GET    | `/api/summary/batches` | List batches |
| GET    | `/api/summary/transactions-per-file` | Tx count per file (charts) |

## Frontend

1. Install and run:

```bash
cd frontend
npm install
npm start
```

2. Open http://localhost:3000. The app uses proxy to `http://localhost:8000` for API calls.

3. Features:

- Upload JSON transaction file
- Overall summary cards (total transactions, amount, unique customers)
- File summary: select batch, see per-file metrics and transaction type distribution
- Charts: Transaction types (pie), Top merchants (bar), Transactions per file (bar), Account activity (bar)

## JSON Format

Expected root structure:

- `batch`, `total_records`, `generated_at`, `date_range` (from/to)
- `transactions`: array of objects with:
  - `transaction_identification` (e.g. `transaction_id`, `reference_number`)
  - `account_information` (e.g. `customer_id`, `account_number`, `account_holder_name`, `email_id`, `mobile_number`)
  - `transaction_details` (e.g. `transaction_date`, `transaction_type`, `transaction_category`)
  - `amount_and_currency` (e.g. `transaction_amount`, `currency_code`)
  - `channel_information` (e.g. `merchant_id`, `merchant_name`, `merchant_category_code`, `location`)
  - `balance_information` (e.g. `closing_balance`, `available_balance`)
  - `transaction_status` (e.g. `status`, `status_code`)

## Validation & Behavior

- **JSON schema**: Root must be an object with a `transactions` array; sample items validated.
- **Duplicate file**: Same `file_name` cannot be uploaded twice (returns 400).
- **Duplicate transaction**: Same `transaction_id` is skipped on insert (no error).
- **Referential integrity**: Customers → Accounts → Transactions; Merchants → Transactions; Batches → Transactions. Rollback on any insert failure.

## Testing (Manual)

1. **Upload**: POST a valid JSON file to `/api/upload/json`; expect 200 and `batch_id`.
2. **Rollback**: Send invalid JSON or trigger DB error; expect 400 and no new batch.
3. **Summary**: GET `/api/summary/file/{batch_id}` and `/api/summary/overall`; verify counts and amounts match expectations.

## ER Diagram

See `docs/ER_DIAGRAM.md` for tables (batches, customers, accounts, merchants, transactions, balances, metadata) and relationships.

## License

Use as needed for the project.
