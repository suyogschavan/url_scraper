from fastapi import FastAPI
from routes import auth, scraping
from models.user_model import create_user_table
from models.scraped_model import create_scraped_table
from dev.devRoutes import router as dev_router
from routes.user import router as user_router

app = FastAPI(title="URL Metadata Scraper", description="Upload CSV & Scrape URLs Metadata")

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



