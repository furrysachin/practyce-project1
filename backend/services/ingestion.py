"""
Ingestion Service - Parses JSON, normalizes data, inserts into PostgreSQL
with referential integrity and batch tracking. Uses DB transactions; rollback on failure.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_
from sqlalchemy.orm import Session

from models import Batch, Customer, Account, Merchant, Transaction, Balance, Metadata
from services.json_parser import (
    extract_balance_from_tx,
    extract_metadata_entries,
    extract_transaction_row,
    parse_banking_json,
    validate_json_structure,
)


class IngestionService:
    """Handles JSON upload, parsing, and normalized insert with batch_id tracking."""

    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_customer(self, data: Dict[str, Any]) -> Customer:
        cid = data["customer_id"]
        existing = self.db.query(Customer).filter(Customer.customer_id == cid).first()
        if existing:
            return existing
        c = Customer(
            customer_id=cid,
            name=data.get("name") or cid,
            email=data.get("email"),
            phone=data.get("phone"),
            pan_number=data.get("pan_number"),
            customer_segment=data.get("customer_segment"),
        )
        self.db.add(c)
        return c

    def _get_or_create_account(self, data: Dict[str, Any]) -> Account:
        acc_num = data["account_number"]
        existing = self.db.query(Account).filter(Account.account_number == acc_num).first()
        if existing:
            return existing
        open_d = data.get("account_open_date")
        if isinstance(open_d, str) and open_d:
            try:
                open_d = datetime.strptime(open_d[:10], "%Y-%m-%d").date()
            except ValueError:
                open_d = None
        a = Account(
            customer_id=data["customer_id"],
            account_number=acc_num,
            account_type=data.get("account_type"),
            status=data.get("status"),
            branch_code=data.get("branch_code"),
            iban=data.get("iban"),
            swift_code=data.get("swift_code"),
            sort_code=data.get("sort_code"),
            account_open_date=open_d,
        )
        self.db.add(a)
        self.db.flush()
        return a

    def _get_or_create_merchant(self, data: Optional[Dict[str, Any]]) -> Optional[Merchant]:
        if not data:
            return None
        mid = data.get("merchant_id")
        if not mid:
            return None
        existing = self.db.query(Merchant).filter(Merchant.merchant_id == mid).first()
        if existing:
            return existing
        m = Merchant(
            merchant_id=mid,
            merchant_name=data.get("merchant_name") or mid,
            category=data.get("category"),
            location=data.get("location"),
        )
        self.db.add(m)
        return m

    def _upsert_balance(self, data: Dict[str, Any]) -> None:
        account_id = data["account_id"]
        existing = self.db.query(Balance).filter(Balance.account_id == account_id).first()
        payload = {
            "current_balance": data.get("current_balance"),
            "available_balance": data.get("available_balance"),
            "ledger_balance": data.get("ledger_balance"),
            "as_of_transaction_id": data.get("as_of_transaction_id"),
        }
        if existing:
            existing.current_balance = payload["current_balance"]
            existing.available_balance = payload["available_balance"]
            existing.ledger_balance = payload["ledger_balance"]
            existing.as_of_transaction_id = payload["as_of_transaction_id"]
        else:
            self.db.add(Balance(account_id=account_id, **payload))

    def _parse_date(self, v: Any) -> Optional[date]:
        if v is None:
            return None
        if isinstance(v, date):
            return v
        s = str(v)[:10]
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except ValueError:
            return None

    def ingest_file(self, file_name: str, data: Dict[str, Any]) -> Tuple[int, Optional[str]]:
        """
        Ingest one JSON file: create batch, parse, insert customers/accounts/merchants/transactions/balances.
        Returns (batch_id, None) on success, (0, error_message) on failure. Uses single DB transaction; rollback on error.
        """
        valid, err = validate_json_structure(data)
        if not valid:
            return 0, err

        batch_info = None
        parsed_items: List[Dict[str, Any]] = []

        try:
            batch_info, parsed_items = parse_banking_json(data, file_name)
        except Exception as e:
            return 0, f"Parse error: {str(e)}"

        # Check duplicate file (idempotency)
        existing_batch = self.db.query(Batch).filter(Batch.file_name == file_name).first()
        if existing_batch:
            return 0, f"Duplicate file: '{file_name}' already uploaded (batch_id={existing_batch.batch_id})"

        try:
            date_from = self._parse_date(batch_info.get("date_from"))
            date_to = self._parse_date(batch_info.get("date_to"))
            gen_at = batch_info.get("generated_at")
            if isinstance(gen_at, str):
                try:
                    gen_at = datetime.fromisoformat(gen_at.replace("Z", "+00:00"))
                except ValueError:
                    gen_at = None

            batch = Batch(
                file_name=file_name,
                source_batch=batch_info.get("source_batch"),
                total_records=batch_info.get("total_records") or len(parsed_items),
                date_from=date_from,
                date_to=date_to,
                generated_at=gen_at,
            )
            self.db.add(batch)
            self.db.flush()
            batch_id = batch.batch_id

            # Metadata entries
            for meta in extract_metadata_entries(batch_id, data):
                self.db.add(Metadata(**meta))

            inserted = 0
            for item in parsed_items:
                customer = self._get_or_create_customer(item["customer"])
                self.db.flush()
                account = self._get_or_create_account(item["account"])
                self.db.flush()
                merchant = self._get_or_create_merchant(item.get("merchant"))
                if merchant:
                    self.db.flush()
                merchant_id = merchant.merchant_id if merchant else None

                tx_row = extract_transaction_row(
                    item["transaction"],
                    batch_id=batch_id,
                    account_id=account.account_id,
                    merchant_id=merchant_id,
                )
                if not tx_row:
                    continue

                # Duplicate transaction prevention: skip if transaction_id already exists
                existing_tx = self.db.query(Transaction).filter(
                    Transaction.transaction_id == tx_row["transaction_id"]
                ).first()
                if existing_tx:
                    continue

                # Normalize date for transaction_date
                td = tx_row.get("transaction_date")
                if isinstance(td, str):
                    tx_row["transaction_date"] = self._parse_date(td) or date(1970, 1, 1)
                elif not isinstance(td, date):
                    tx_row["transaction_date"] = date(1970, 1, 1)

                self.db.add(Transaction(**tx_row))
                inserted += 1

                # Update balance snapshot for this account
                bal_data = extract_balance_from_tx(
                    item["transaction"],
                    account_id=account.account_id,
                    transaction_id=tx_row["transaction_id"],
                )
                self._upsert_balance(bal_data)

            self.db.commit()
            return batch_id, None

        except Exception as e:
            self.db.rollback()
            return 0, f"Ingestion failed: {str(e)}"
