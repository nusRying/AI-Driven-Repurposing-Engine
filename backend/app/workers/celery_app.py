from celery import Celery
from ..config import settings

celery_app = Celery(
    "repurposing_engine",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.scrape_task",
        "app.workers.script_task",
        "app.workers.audio_task",
        "app.workers.video_task"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

if __name__ == "__main__":
    celery_app.start()
