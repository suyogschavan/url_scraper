from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram
from routes import auth, scraping
from models.user_model import create_user_table
from models.scraped_model import create_scraped_table
from dev.devRoutes import router as dev_router
from routes.user import router as user_router

app = FastAPI(title="URL Metadata Scraper", description="Upload CSV & Scrape URLs Metadata")

create_user_table()
create_scraped_table()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scraping.router, prefix="/scraper", tags=["Scraping"])
app.include_router(dev_router, prefix="/dev", tags=["Development"])
app.include_router(user_router, prefix="/user", tags=["User"])

request_duration = Histogram('fastapi_request_duration_seconds', 'Duration of FastAPI requests in seconds')

Instrumentator().instrument(app).expose(app)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    with request_duration.time():
        response = await call_next(request)
    return response

@app.get("/")
def home():
    return {"message": "Welcome to the URL Scraper API 🚀"}




