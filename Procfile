fastAPI: uvicorn realmain:app --host 0.0.0.0 --port 8000 --reload
celery-worker: celery -A utils.celery_worker.celery_app worker --loglevel=info -P gevent
```

