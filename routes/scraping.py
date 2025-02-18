from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
import pandas as pd
import io
from db.connection import get_db_connection
from utils.auth_utils import decode_token
from fastapi.security import OAuth2PasswordBearer
from utils.celery_worker import celery_app


router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/upload")
async def upload_csv(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    user_data = decode_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
    print()
    li = df.to_dict(orient='records'), user_data["user_id"]
    data = li[0]
    urls = []
    print(celery_app.control.ping())
    for i in data:
        urls.append(i["url"])
    print(urls)
    try:
        if not celery_app.control.ping():
            raise HTTPException(status_code=500, detail="Cannot connect to Celery or Redis")
        task = celery_app.send_task('utils.tasks.scrape_urls', args=[urls, user_data["user_id"]])
        return {"task_id": task.id}
    except Exception as e:
        return {"Error : ", e}

@router.get("/status/{task_id}")
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


@router.get("results/{task_id}")
def get_task_results(task_id: str):
    data = celery_app.AsyncResult(task_id)
    return {"taskInfo": data.result}