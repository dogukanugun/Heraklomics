from celery import Celery

celery_app = Celery(
    "heraclomics_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["tasks.run_pipeline"]
)

celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 3600  # 1 hour
