from celery import Celery
from dotenv import load_dotenv
import os

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
    task_time_limit=300, 
    task_soft_time_limit=240,  
)
import utils.tasks