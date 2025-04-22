
# backend/app/api/files.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from pathlib import Path
from typing import Literal, Optional
from app.dependencies import get_current_user
from app.db.models import User, UploadRecord
from app.db.session import get_db
from app.db.crud import create_upload_record, update_upload_status
from app.schemas.analysis import UploadRecordResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from tasks.run_pipeline import run_pipeline  # Celery task import
from app.schemas.analysis import SarekRunOptions


router = APIRouter()
BASE_UPLOAD_DIR = Path("data/uploads")

@router.post("/upload", response_model=UploadRecordResponse)
async def upload_file(
    analysis_type: Literal["wes", "wgs", "rnaseq", "scrnaseq"] = Query(...),
    local_kw: Optional[str] = Query(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    allowed_extensions = {
        "wes": [".fastq", ".fastq.gz", ".bam", ".cram", ".vcf", ".vcf.gz"],
        "wgs": [".fastq", ".fastq.gz", ".bam", ".cram", ".vcf", ".vcf.gz"],
        "rnaseq": [".fastq", ".fastq.gz"],
        "scrnaseq": [".h5", ".h5ad", ".loom", ".mtx", ".mtx.gz", ".csv", ".tsv", ".txt", ".rds"],
    }

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions[analysis_type]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension for {analysis_type}. Allowed: {allowed_extensions[analysis_type]}"
        )

    user_dir = BASE_UPLOAD_DIR / current_user.username / analysis_type
    user_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    file_path = user_dir / filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Save upload record in DB
    upload_record = await create_upload_record(
        db,
        user_id=current_user.id,
        analysis_type=analysis_type,
        filename=file.filename,
        saved_path=str(file_path),
    )

    return upload_record




router = APIRouter()

@router.post("/run/{upload_id}")
async def trigger_pipeline(
    upload_id: int,
    opts: SarekRunOptions,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    upload = await db.get(UploadRecord, upload_id)
    if not upload or upload.user_id != current_user.id:
        raise HTTPException(404, "Upload not found")
    if upload.status != "uploaded":
        raise HTTPException(400, f"Cannot start: status is {upload.status}")

    # enqueue with mode + any advanced args
    run_pipeline.delay(
        upload_id=upload_id,
        file_path=upload.saved_path,
        analysis_type=upload.analysis_type,
        opts=opts.dict()
    )
    await update_upload_status(db, upload_id, "queued")
    return {"message": "Pipeline queued", "upload_id": upload_id}
