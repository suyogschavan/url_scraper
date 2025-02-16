from fastapi import FastAPI
from routes import auth, scraping
from models.user_model import create_user_table
from models.scraped_model import create_scraped_table

app = FastAPI(title="URL Metadata Scraper", description="Upload CSV & Scrape URLs Metadata")

# Initialize database tables
create_user_table()
create_scraped_table()

# Include Routes
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(scraping.router, prefix="/scraper", tags=["Scraping"])

@app.get("/")
def home():
    return {"message": "Welcome to the URL Scraper API 🚀"}



