"""
POST /upload-json - Upload JSON file, parse, normalize, insert with batch_id.
"""
import json
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from sqlalchemy.orm import Session

from database import get_db
from services import IngestionService

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/json")
def upload_json(
    file: UploadFile = File(..., description="JSON file with banking transactions"),
    db: Session = Depends(get_db),
):
    """
    Upload a JSON file containing retail banking transactions.
    Parses nested structure, normalizes into DB schema, inserts with referential integrity.
    Uses a single DB transaction; rolls back on any failure.
    Prevents duplicate file uploads (by file_name) and duplicate transactions (by transaction_id).
    Returns batch_id and counts on success.
    """
    if not file.filename or not file.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be a .json file")

    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    service = IngestionService(db)
    batch_id, error = service.ingest_file(file.filename or "unknown.json", data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return {
        "status": "success",
        "message": "File ingested successfully",
        "batch_id": batch_id,
        "file_name": file.filename,
    }
