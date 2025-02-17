from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
REDIS_URL = os.getenv("REDIS_URL") # for depolyment
# REDIS_URL = "redis://localhost:6379/0" # for depolyment


celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

import utils.tasks