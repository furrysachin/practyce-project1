"""
Summary APIs: file summary and overall summary.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from services import AnalyticsService

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("/file/{batch_id}")
def get_file_summary(batch_id: int, db: Session = Depends(get_db)):
    """
    File summary for a given batch_id.
    Returns: total_transactions, total_amount, unique_customers, transaction_type_distribution.
    """
    service = AnalyticsService(db)
    result = service.get_file_summary(batch_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found")
    return result


@router.get("/overall")
def get_overall_summary(db: Session = Depends(get_db)):
    """
    Overall analytics across all uploaded files.
    Returns: total_transactions_all_files, total_transaction_volume, top_merchants,
    most_active_accounts, customer_activity_summary.
    """
    service = AnalyticsService(db)
    return service.get_overall_summary()


@router.get("/batches")
def list_batches(db: Session = Depends(get_db)):
    """List all batches (for dashboard file selector)."""
    service = AnalyticsService(db)
    return service.get_batches_list()


@router.get("/transactions-per-file")
def transactions_per_file(db: Session = Depends(get_db)):
    """Transaction count per file/batch for charts."""
    service = AnalyticsService(db)
    return service.get_transactions_per_file()
