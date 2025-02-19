import logging
from celery import group
import requests
from bs4 import BeautifulSoup
from db.connection import get_db_connection
from dotenv import load_dotenv
import os
from utils.celery_worker import celery_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

@celery_app.task
def scrape_metadata(url):
    """Scrapes metadata for a given URL."""
    try:
        logger.info(f"Fetching metadata for: {url}")
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            logger.warning(f"Cannot access URL {url} (Status Code: {response.status_code})")
            return {"url": url, "title": "No Title", "description": "No Description", "keywords": "No Keywords"}

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No Title"
        description = soup.find("meta", attrs={"name": "description"})
        keywords = soup.find("meta", attrs={"name": "keywords"})

        metadata = {
            "url": url,
            "title": title,
            "description": description["content"] if description else "No Description",
            "keywords": keywords["content"] if keywords else "No Keywords"
        }

        logger.info(f"Metadata extracted successfully for {url}")
        return metadata

    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {"url": url, "title": "No Title", "description": "No Description", "keywords": "No Keywords"}

@celery_app.task
def insert_into_db(data_to_insert):
    """Inserts scraped data into the database asynchronously."""
    if not data_to_insert:
        logger.info("No data to insert into the database.")
        return

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        logger.info(f"Inserting {len(data_to_insert)} records into the database.")

        cur.executemany(
            "INSERT INTO scraped_data (user_id, url, title, description, keywords) VALUES (%s, %s, %s, %s, %s);",
            data_to_insert
        )

        conn.commit()
        logger.info("Database commit successful.")
    except Exception as db_error:
        logger.error(f"Database error: {db_error}")
    finally:
        cur.close()
        conn.close()
        logger.info("Database connection closed.")

@celery_app.task(bind=True)
def scrape_urls(self, urls, user_id):
    """Scrapes a list of URLs in parallel using Celery's group processing."""
    logger.info(f"Starting parallel scraping task for user_id={user_id} with {len(urls)} URLs.")

    # Use Celery's group feature to scrape URLs in parallel
    scraping_tasks = group(scrape_metadata.s(url) for url in urls)
    results = scraping_tasks.apply_async()
    
    metadata_results = results.get()

    data_to_insert = [(user_id, meta["url"], meta["title"], meta["description"], meta["keywords"]) for meta in metadata_results]

    insert_into_db.delay(data_to_insert)

    return {"status": "Scraping completed", "total_scraped": len(metadata_results)}


from celery import shared_task

@shared_task
def test_celery():
    logger.info("Test Celery task executed.")
    return "Celery is working!"
