"""
Validation tests: JSON schema, duplicate prevention, summary correctness.
Run from backend directory: python -m pytest tests/ -v
"""
import json
import pytest
from services.json_parser import validate_json_structure, parse_banking_json, extract_batch_info


def test_validate_json_structure_valid():
    data = {
        "batch": "BATCH_001",
        "transactions": [
            {
                "transaction_identification": {"transaction_id": "TX1"},
                "account_information": {"customer_id": "C1", "account_number": "123"},
            }
        ],
    }
    valid, err = validate_json_structure(data)
    assert valid is True
    assert err is None


def test_validate_json_structure_missing_transactions():
    valid, err = validate_json_structure({"batch": "B"})
    assert valid is False
    assert "transactions" in err


def test_validate_json_structure_root_not_object():
    valid, err = validate_json_structure([])
    assert valid is False
    assert "object" in err


def test_validate_json_structure_transactions_not_array():
    valid, err = validate_json_structure({"transactions": "not-array"})
    assert valid is False


def test_parse_banking_json_extracts_batch_info():
    data = {
        "batch": "BATCH_007",
        "total_records": 10,
        "date_range": {"from": "2020-01-01", "to": "2020-12-31"},
        "generated_at": "2026-01-01T00:00:00",
        "transactions": [],
    }
    batch_info, items = parse_banking_json(data, "test.json")
    assert batch_info["file_name"] == "test.json"
    assert batch_info["source_batch"] == "BATCH_007"
    assert batch_info["total_records"] == 10
    assert len(items) == 0


def test_parse_banking_json_extracts_one_tx():
    data = {
        "batch": "B",
        "transactions": [
            {
                "transaction_identification": {"transaction_id": "TX1", "reference_number": "R1"},
                "account_information": {
                    "customer_id": "CIF1",
                    "account_holder_name": "John",
                    "account_number": "ACC1",
                    "email_id": "j@x.com",
                    "mobile_number": "999",
                },
                "transaction_details": {
                    "transaction_date": "2020-01-15",
                    "transaction_type": "Debit",
                    "transaction_category": "Retail",
                },
                "amount_and_currency": {"transaction_amount": 100.50, "currency_code": "INR"},
                "channel_information": {
                    "merchant_id": "M1",
                    "merchant_name": "Store",
                    "merchant_category_code": "5411",
                    "location": "City",
                },
                "balance_information": {"closing_balance": 5000, "available_balance": 4800},
                "transaction_status": {"status": "Completed"},
            }
        ],
    }
    batch_info, items = parse_banking_json(data, "f.json")
    assert len(items) == 1
    assert items[0]["customer"]["customer_id"] == "CIF1"
    assert items[0]["account"]["account_number"] == "ACC1"
    assert items[0]["merchant"]["merchant_id"] == "M1"
