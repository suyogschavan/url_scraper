from celery import Celery
from dotenv import load_dotenv
import os
from celery_prometheus_exporter import setup_metrics
from prometheus_client import start_http_server, Counter, Gauge
import time

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL")
celery_app = Celery(
    'tasks',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=False,
)

TASKS_STARTED = Counter("celery_tasks_started", "Number of tasks started")
TASKS_COMPLETED = Counter("celery_tasks_completed", "Number of tasks completed")
TASKS_FAILED = Counter("celery_tasks_failed", "Number of failed tasks")
TASKS_ACTIVE = Gauge("celery_tasks_active", "Number of active Celery tasks")

start_http_server(8001)

setup_metrics(celery_app)
@celery_app.task(bind=True)
def example_task(self):
    TASKS_STARTED.inc()
    TASKS_ACTIVE.inc()
    try:
        time.sleep(2)  
        TASKS_COMPLETED.inc()
    except Exception:
        TASKS_FAILED.inc()
    finally:
        TASKS_ACTIVE.dec()
    return "Task Done!"
import utils.tasks
