from celery import Celery
from config import settings

celery_app = Celery(
    "meta_ads_analyzer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.services.celery_tasks']  # Auto-discover tasks
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Import tasks to register them
from app.services import celery_tasks
