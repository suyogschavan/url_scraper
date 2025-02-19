from fastapi import FastAPI
from routes import auth, scraping
from models.user_model import create_user_table
from models.scraped_model import create_scraped_table
from dev.devRoutes import router as dev_router
from routes.user import router as user_router
import redis
import os
# from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="URL Metadata Scraper", description="Upload CSV & Scrape URLs Metadata")



# Instrumentator().instrument(app).expose(app)

create_user_table()
create_scraped_table()

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scraping.router, prefix="/scraper", tags=["Scraping"])
app.include_router(dev_router, prefix="/dev", tags=["Development"])
app.include_router(user_router, prefix="/user", tags=["User"])

@app.get("/", include_in_schema=False)
def home():
    return {"message": "Welcome to the URL Scraper API 🚀"}




