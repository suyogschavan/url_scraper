from fastapi import FastAPI
from routes import auth, scraping
from models.user_model import create_user_table
from models.scraped_model import create_scraped_table
from dev.devRoutes import router as dev_router
from routes.user import router as user_router
import redis
import os

app = FastAPI(title="URL Metadata Scraper", description="Upload CSV & Scrape URLs Metadata")

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_client = redis.Redis.from_url(redis_url)

# Initialize database tables
create_user_table()
create_scraped_table()

# Include Routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scraping.router, prefix="/scraper", tags=["Scraping"])
app.include_router(dev_router, prefix="/dev", tags=["Development"])
app.include_router(user_router, prefix="/user", tags=["User"])

@app.get("/")
def home():
    return {"message": "Welcome to the URL Scraper API 🚀"}

@app.get("/test-redis")
def test_redis():
    try:
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        return {"message": "Redis is working!", "value": value.decode("utf-8")}
    except Exception as e:
        return {"error": str(e)}



