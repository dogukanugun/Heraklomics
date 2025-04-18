from celery import shared_task
from pathlib import Path
import subprocess
from app.db.session import SessionLocal
from app.db.crud import update_upload_status

@shared_task(bind=True)
def run_pipeline(self, upload_id: int, file_path: str, analysis_type: str):
    db = SessionLocal()

    try:
        update_upload_status_sync(db, upload_id, "processing")

        result_dir = Path(file_path).parent.parent / "results" / str(upload_id)
        log_path = result_dir / "logs"
        log_path.mkdir(parents=True, exist_ok=True)
        log_file = log_path / "pipeline.log"

        # Run Nextflow pipeline
        with open(log_file, "w") as log:
            process = subprocess.Popen(
                ["nextflow", "run", f"pipelines/{analysis_type}/main.nf", "--input", file_path, "--outdir", str(result_dir)],
                stdout=log, stderr=log
            )
            process.wait()

        if process.returncode == 0:
            update_upload_status_sync(db, upload_id, "done")
        else:
            update_upload_status_sync(db, upload_id, "failed")

    except Exception as e:
        update_upload_status_sync(db, upload_id, "failed")
        raise e
    finally:
        db.close()

# sync helper
def update_upload_status_sync(db, upload_id: int, status: str):
    from app.db.models import UploadRecord
    from sqlalchemy import update
    db.execute(
        update(UploadRecord).where(UploadRecord.id == upload_id).values(status=status)
    )
    db.commit()
