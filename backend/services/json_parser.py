"""
JSON Parser & Transformer - Normalizes nested banking transaction JSON
into flat structures for relational insert.
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from decimal import Decimal


def _parse_date(value: Any) -> Optional[datetime]:
    """Parse date/datetime string to datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    s = str(value).strip()
    if not s:
        return None
    s = s.replace("+05:30", "").replace("Z", "").split(".")[0]
    if "T" in s:
        try:
            return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            pass
    try:
        return datetime.strptime(s[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _date_only(dt: Optional[datetime]) -> Optional[str]:
    """Return YYYY-MM-DD for date column."""
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d") if hasattr(dt, "strftime") else str(dt)[:10]


def _decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except Exception:
        return None


def _str(value: Any, max_len: int = 0) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if max_len and len(s) > max_len:
        s = s[:max_len]
    return s or None


def extract_batch_info(data: Dict[str, Any], file_name: str) -> Dict[str, Any]:
    """Extract batch-level fields from root JSON."""
    date_range = data.get("date_range") or {}
    generated_at = data.get("generated_at")
    return {
        "file_name": file_name,
        "source_batch": _str(data.get("batch"), 64),
        "total_records": int(data.get("total_records") or 0),
        "date_from": _date_only(_parse_date(date_range.get("from"))),
        "date_to": _date_only(_parse_date(date_range.get("to"))),
        "generated_at": _parse_date(generated_at),
    }


def extract_customer_from_tx(tx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract customer row from transaction's account_information."""
    acc = tx.get("account_information") or {}
    customer_id = _str(acc.get("customer_id"), 32)
    if not customer_id:
        return None
    return {
        "customer_id": customer_id,
        "name": _str(acc.get("account_holder_name") or acc.get("customer_id"), 256) or customer_id,
        "email": _str(acc.get("email_id"), 256),
        "phone": _str(acc.get("mobile_number"), 32),
        "pan_number": _str(acc.get("pan_number"), 32),
        "customer_segment": _str(acc.get("customer_segment"), 64),
    }


def extract_account_from_tx(tx: Dict[str, Any], customer_id: str) -> Optional[Dict[str, Any]]:
    """Extract account row from transaction's account_information."""
    acc = tx.get("account_information") or {}
    account_number = _str(acc.get("account_number"), 64)
    if not account_number:
        return None
    open_date = acc.get("account_open_date")
    return {
        "customer_id": customer_id,
        "account_number": account_number,
        "account_type": _str(acc.get("account_type"), 64),
        "status": _str(acc.get("account_status"), 32),
        "branch_code": _str(acc.get("branch_code"), 32),
        "iban": _str(acc.get("iban"), 64),
        "swift_code": _str(acc.get("swift_code"), 32),
        "sort_code": _str(acc.get("sort_code"), 32),
        "account_open_date": _date_only(_parse_date(open_date)) if open_date else None,
    }


def extract_merchant_from_tx(tx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Extract merchant row from transaction's channel_information."""
    ch = tx.get("channel_information") or {}
    merchant_id = _str(ch.get("merchant_id"), 32)
    if not merchant_id:
        return None
    return {
        "merchant_id": merchant_id,
        "merchant_name": _str(ch.get("merchant_name"), 256) or merchant_id,
        "category": _str(ch.get("merchant_category_code"), 32),
        "location": _str(ch.get("location"), 128),
    }


def extract_transaction_row(
    tx: Dict[str, Any],
    batch_id: int,
    account_id: int,
    merchant_id: Optional[str],
) -> Optional[Dict[str, Any]]:
    """Extract transaction row for DB insert."""
    ident = tx.get("transaction_identification") or {}
    details = tx.get("transaction_details") or {}
    amount_curr = tx.get("amount_and_currency") or {}
    status_block = tx.get("transaction_status") or {}
    ch = tx.get("channel_information") or {}

    transaction_id = _str(ident.get("transaction_id"), 64)
    if not transaction_id:
        return None

    tx_date = details.get("transaction_date") or details.get("transaction_datetime")
    dt = _parse_date(tx_date)

    return {
        "transaction_id": transaction_id,
        "batch_id": batch_id,
        "account_id": account_id,
        "merchant_id": merchant_id,
        "reference_number": _str(ident.get("reference_number"), 64),
        "transaction_date": _date_only(dt) or "1970-01-01",
        "transaction_datetime": _parse_date(details.get("transaction_datetime") or tx_date),
        "transaction_type": _str(details.get("transaction_type"), 64),
        "transaction_category": _str(details.get("transaction_category"), 128),
        "transaction_code": _str(details.get("transaction_code"), 32),
        "currency_code": _str(amount_curr.get("currency_code"), 8) or "INR",
        "transaction_amount": _decimal(amount_curr.get("transaction_amount")) or Decimal("0"),
        "net_amount": _decimal(amount_curr.get("net_amount")),
        "status": _str(status_block.get("status"), 32),
        "status_code": _str(status_block.get("status_code"), 16),
        "payment_network": _str(details.get("payment_network"), 32),
        "channel_type": _str(ch.get("channel_type"), 64),
    }


def extract_balance_from_tx(
    tx: Dict[str, Any],
    account_id: int,
    transaction_id: str,
) -> Dict[str, Any]:
    """Extract balance snapshot from transaction's balance_information."""
    bal = tx.get("balance_information") or {}
    return {
        "account_id": account_id,
        "current_balance": _decimal(bal.get("closing_balance")),
        "available_balance": _decimal(bal.get("available_balance")),
        "ledger_balance": _decimal(bal.get("ledger_balance")),
        "as_of_transaction_id": transaction_id,
    }


def extract_metadata_entries(batch_id: int, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build metadata key-value list for batch."""
    entries = []
    if data.get("batch"):
        entries.append({"batch_id": batch_id, "meta_key": "source_batch", "meta_value": str(data["batch"])})
    if data.get("total_records") is not None:
        entries.append({"batch_id": batch_id, "meta_key": "total_records", "meta_value": str(data["total_records"])})
    dr = data.get("date_range") or {}
    if dr.get("from"):
        entries.append({"batch_id": batch_id, "meta_key": "date_from", "meta_value": str(dr["from"])})
    if dr.get("to"):
        entries.append({"batch_id": batch_id, "meta_key": "date_to", "meta_value": str(dr["to"])})
    if data.get("generated_at"):
        entries.append({"batch_id": batch_id, "meta_key": "generated_at", "meta_value": str(data["generated_at"])})
    return entries


def parse_banking_json(data: Dict[str, Any], file_name: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Parse full JSON payload into batch info and list of normalized transaction payloads.
    Each payload has: customer, account, merchant, transaction, balance.
    Caller will resolve account_id/merchant_id and set batch_id when inserting.
    """
    batch_info = extract_batch_info(data, file_name)
    transactions_raw = data.get("transactions") or []
    if not isinstance(transactions_raw, list):
        transactions_raw = []

    result: List[Dict[str, Any]] = []
    for tx in transactions_raw:
        if not isinstance(tx, dict):
            continue
        customer = extract_customer_from_tx(tx)
        if not customer:
            continue
        account = extract_account_from_tx(tx, customer["customer_id"])
        if not account:
            continue
        merchant = extract_merchant_from_tx(tx)
        result.append({
            "customer": customer,
            "account": account,
            "merchant": merchant,
            "transaction": tx,
            "balance": None,
        })
        # transaction row and balance need batch_id, account_id, merchant_id - filled during insert

    return batch_info, result


def validate_json_structure(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Basic JSON schema validation. Returns (valid, error_message).
    """
    if not isinstance(data, dict):
        return False, "Root must be a JSON object"
    if "transactions" not in data:
        return False, "Missing 'transactions' array"
    if not isinstance(data["transactions"], list):
        return False, "'transactions' must be an array"
    for i, tx in enumerate(data["transactions"][:3]):  # sample first 3
        if not isinstance(tx, dict):
            return False, f"transactions[{i}] must be an object"
        if "transaction_identification" not in tx and "account_information" not in tx:
            return False, f"transactions[{i}] must contain transaction_identification and account_information"
    return True, None
