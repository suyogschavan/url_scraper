from celery import Celery
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from db.connection import get_db_connection
from dotenv import load_dotenv
import os
from utils.celery_worker import celery_app
import asyncio
import aiohttp
import logging

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
@celery_app.task(bind=True)
def scrape_urls(self, urls, user_id):
    logger.info(f"Starting scrape_urls task for user_id: {user_id}")
    asyncio.run(scrape_and_store(urls, user_id, self.request.id))

async def scrape_and_store(urls, user_id, task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    tasks = [scrape_metadata(url) for url in urls]
    results = await asyncio.gather(*tasks)

    for metadata in results:
        if metadata:
            cur.execute(
                "INSERT INTO scraped_data (user_id, task_id, url, title, description, keywords) VALUES (%s, %s, %s, %s, %s, %s);",
                (user_id, task_id, metadata["url"], metadata["title"], metadata["description"], metadata["keywords"])
            )
    
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"Completed scrape_urls task for user_id: {user_id}")

async def scrape_metadata(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=40) as response: # type: ignore
                if response.status != 200:
                    return {
                        "url": url,
                        "title": "No Title",
                        "description": "No Description",
                        "keywords": "No Keywords"
                    }

                text = await response.text()
                soup = BeautifulSoup(text, "html.parser")
                title = soup.title.string if soup.title else "No Title"
                description = soup.find("meta", attrs={"name": "description"})
                keywords = soup.find("meta", attrs={"name": "keywords"})

                return {
                    "url": url,
                    "title": title,
                    "description": description["content"] if description else "No Description",
                    "keywords": keywords["content"] if keywords else "No Keywords"
                }
    except Exception as e:
        return {
            "url": url,
            "title": "No Title",
            "description": "No Description",
            "keywords": "No Keywords"
        }

from celery import shared_task

@shared_task
def test_celery():
    return "Celery is working!"
