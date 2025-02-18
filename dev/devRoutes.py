from fastapi import APIRouter, BackgroundTasks
from db.connection import get_db_connection
from utils.tasks import test_celery
import redis
import time
import os

router = APIRouter()
redis_url = os.getenv('REDIS_URL')
redis_client = redis.Redis.from_url(redis_url)

@router.get("/getUsers")
def getUsers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

@router.get("/getScrapedData")
def getScrapedData():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scraped_data;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def background_ping():
    while True:
        time.sleep(500)  
        print("Keeping FastAPI alive...")

@router.get("/keep-alive")
async def keep_alive(background_tasks: BackgroundTasks):
    background_tasks.add_task(background_ping)
    return {"status": "alive"}

@router.get("/test-redis")
def test_redis():
    try:
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        return {"message": "Redis is working!", "value": value.decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}

@router.get("/test-celery")
def test_celery_endpoint():
    task = test_celery.delay()
    return {"task_id": task.id}