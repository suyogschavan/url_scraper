from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
import pandas as pd
import io
from db.connection import get_db_connection
from utils.auth_utils import decode_token
from fastapi.security import OAuth2PasswordBearer
from utils.celery_worker import celery_app
from utils.tasks import test_celery
import logging

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    logger.info("Received upload-csv request")
    user_data = decode_token(token)
    if not user_data:
        logger.warning("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    data = df.to_dict(orient='records')
    urls = [record["url"] for record in data]

    try:
        if not celery_app.control.ping():
            logger.error("Cannot connect to Celery or Redis")
            raise HTTPException(status_code=500, detail="Cannot connect to Celery or Redis")

        task = celery_app.send_task('utils.tasks.scrape_urls', args=[urls, user_data["user_id"]])

        logger.info(f"Created task with ID: {task.id}")
        return {"task_id": task.id}  
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"Error": str(e)}


@router.get("/task-status/{task_id}")
def get_task_status(task_id: str):
    task = celery_app.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        response = {
            'state': task.state,
            'error': str(task.info),
        }
    return response

@router.get("/results/{task_id}")
def get_results(task_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scraped_data WHERE task_id = %s;", (task_id,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for the given task_id")
    return results