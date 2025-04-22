from celery import shared_task
from pathlib import Path
import subprocess
from app.db.session import SessionLocal
from app.db.crud import update_upload_status_sync

# curated defaults
DEFAULTS = {
    "curated_germline": {
        "aligner": "bwa-mem2",
        "variant_callers": ["HaplotypeCaller","FreeBayes"],
        "svtools": ["Manta"],
        "cnvtools": ["CNVKit"],
        "annotators": ["VEP"]
    },
    "curated_somatic": {
        "aligner": "bwa-mem2",
        "variant_callers": ["Mutect2","Strelka2"],
        "svtools": ["Manta"],
        "cnvtools": ["Control-FREEC"],
        "annotators": ["VEP"]
    }
}

@shared_task(bind=True)
def run_pipeline(self, upload_id: int, file_path: str, analysis_type: str, opts: dict):
    db = SessionLocal()
    try:
        update_upload_status_sync(db, upload_id, "processing")
        mode = opts["mode"]
        params = opts if mode.startswith("advanced") else DEFAULTS[mode]

        result_dir = Path(file_path).parent.parent / "results" / str(upload_id)
        log_file = result_dir / "logs" / "pipeline.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "nextflow", "run", "nf-core/sarek", "-r", "3.5.1", "-profile", "docker",
            "--input", file_path,
            "--outdir", str(result_dir),
            "--aligner", params["aligner"],
            "--tools", ",".join(params["variant_callers"])
        ]
        if p := params.get("svtools"):   cmd += ["--svtools", ",".join(p)]
        if p := params.get("cnvtools"):  cmd += ["--cnvtools", ",".join(p)]
        if p := params.get("annotators"):cmd += ["--annotation_tools", ",".join(p)]

        with open(log_file, "w") as lf:
            proc = subprocess.Popen(cmd, stdout=lf, stderr=lf)
            proc.wait()

        status = "done" if proc.returncode == 0 else "failed"
        update_upload_status_sync(db, upload_id, status)

    except Exception:
        update_upload_status_sync(db, upload_id, "failed")
        raise
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
