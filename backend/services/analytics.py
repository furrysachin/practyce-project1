"""
Analytics Service - Optimized SQL queries for summary and reporting.
"""
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from models import Batch, Customer, Account, Merchant, Transaction


class AnalyticsService:
    """Summary and analytics queries."""

    def __init__(self, db: Session):
        self.db = db

    def get_file_summary(self, batch_id: int) -> Optional[Dict[str, Any]]:
        """
        GET /summary/file/{batch_id}
        total_transactions, total_amount, unique_customers, transaction_type_distribution
        """
        batch = self.db.query(Batch).filter(Batch.batch_id == batch_id).first()
        if not batch:
            return None

        # Total transactions and total amount for this batch
        tx_agg = self.db.query(
            func.count(Transaction.transaction_id).label("total_transactions"),
            func.coalesce(func.sum(Transaction.transaction_amount), 0).label("total_amount"),
        ).filter(Transaction.batch_id == batch_id).first()

        # Unique customers (via accounts) in this batch
        unique_customers = self.db.query(func.count(func.distinct(Account.customer_id))).select_from(
            Transaction
        ).join(Account, Transaction.account_id == Account.account_id).filter(
            Transaction.batch_id == batch_id
        ).scalar() or 0

        # Transaction type distribution
        type_dist = self.db.query(
            Transaction.transaction_type,
            func.count(Transaction.transaction_id).label("count"),
        ).filter(Transaction.batch_id == batch_id).group_by(
            Transaction.transaction_type
        ).all()

        return {
            "batch_id": batch_id,
            "file_name": batch.file_name,
            "source_batch": batch.source_batch,
            "total_transactions": tx_agg.total_transactions or 0,
            "total_amount": float(tx_agg.total_amount or 0),
            "unique_customers": unique_customers,
            "transaction_type_distribution": [
                {"transaction_type": t or "Unknown", "count": c}
                for t, c in type_dist
            ],
        }

    def get_overall_summary(self) -> Dict[str, Any]:
        """
        GET /summary/overall
        total_transactions_all_files, total_transaction_volume, top_merchants,
        most_active_accounts, customer_activity_summary
        """
        # Total transactions and volume across all batches
        tx_agg = self.db.query(
            func.count(Transaction.transaction_id).label("total_transactions"),
            func.coalesce(func.sum(Transaction.transaction_amount), 0).label("total_volume"),
        ).first()

        # Top 10 merchants by transaction count
        top_merchants = self.db.query(
            Merchant.merchant_name,
            Merchant.merchant_id,
            func.count(Transaction.transaction_id).label("tx_count"),
            func.coalesce(func.sum(Transaction.transaction_amount), 0).label("total_amount"),
        ).join(Transaction, Transaction.merchant_id == Merchant.merchant_id).group_by(
            Merchant.merchant_id, Merchant.merchant_name
        ).order_by(
            func.count(Transaction.transaction_id).desc()
        ).limit(10).all()

        # Most active accounts (by transaction count)
        most_active = self.db.query(
            Account.account_id,
            Account.account_number,
            Account.account_type,
            func.count(Transaction.transaction_id).label("tx_count"),
        ).join(Transaction, Transaction.account_id == Account.account_id).group_by(
            Account.account_id, Account.account_number, Account.account_type
        ).order_by(
            func.count(Transaction.transaction_id).desc()
        ).limit(10).all()

        # Customer activity summary: unique customers, and per-customer tx count (sample)
        unique_customers = self.db.query(func.count(func.distinct(Account.customer_id))).scalar() or 0
        customer_activity = self.db.query(
            Account.customer_id,
            func.count(Transaction.transaction_id).label("tx_count"),
            func.coalesce(func.sum(Transaction.transaction_amount), 0).label("total_amount"),
        ).join(Transaction, Transaction.account_id == Account.account_id).group_by(
            Account.customer_id
        ).order_by(
            func.count(Transaction.transaction_id).desc()
        ).limit(20).all()

        return {
            "total_transactions_all_files": tx_agg.total_transactions or 0,
            "total_transaction_volume": float(tx_agg.total_volume or 0),
            "unique_customers_overall": unique_customers,
            "top_merchants": [
                {
                    "merchant_id": m.merchant_id,
                    "merchant_name": m.merchant_name,
                    "transaction_count": m.tx_count,
                    "total_amount": float(m.total_amount or 0),
                }
                for m in top_merchants
            ],
            "most_active_accounts": [
                {
                    "account_id": a.account_id,
                    "account_number": a.account_number,
                    "account_type": a.account_type,
                    "transaction_count": a.tx_count,
                }
                for a in most_active
            ],
            "customer_activity_summary": [
                {
                    "customer_id": c.customer_id,
                    "transaction_count": c.tx_count,
                    "total_amount": float(c.total_amount or 0),
                }
                for c in customer_activity
            ],
        }

    def get_batches_list(self) -> List[Dict[str, Any]]:
        """List all batches for dashboard dropdown/list."""
        rows = self.db.query(Batch).order_by(Batch.uploaded_at.desc()).all()
        return [
            {
                "batch_id": b.batch_id,
                "file_name": b.file_name,
                "source_batch": b.source_batch,
                "total_records": b.total_records,
                "uploaded_at": b.uploaded_at.isoformat() if b.uploaded_at else None,
            }
            for b in rows
        ]

    def get_transactions_per_file(self) -> List[Dict[str, Any]]:
        """For chart: transaction count per batch/file."""
        rows = self.db.query(
            Batch.batch_id,
            Batch.file_name,
            func.count(Transaction.transaction_id).label("count"),
        ).outerjoin(Transaction, Transaction.batch_id == Batch.batch_id).group_by(
            Batch.batch_id, Batch.file_name
        ).order_by(Batch.batch_id).all()
        return [
            {"batch_id": r.batch_id, "file_name": r.file_name, "transaction_count": r.count}
            for r in rows
        ]
