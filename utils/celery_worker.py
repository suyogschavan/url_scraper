from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

# Load environment variables
REDIS_URL = os.getenv("REDIS_URL")
# REDIS_URL = "redis://default:boNKq12QB2dnyZ6Y34RrL0u7t8s7ACu0@redis-19889.c322.us-east-1-2.ec2.redns.redis-cloud.com:19889"

celery_app = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

import utils.tasks