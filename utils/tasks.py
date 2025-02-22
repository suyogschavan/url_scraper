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
    total_urls = len(urls)
    asyncio.run(scrape_and_store(self, urls, user_id, self.request.id, total_urls))

async def scrape_and_store(self, urls, user_id, task_id, total_urls):
    conn = get_db_connection()
    cur = conn.cursor()
    tasks = [scrape_metadata(url) for url in urls]
    results = []

    for i, task in enumerate(asyncio.as_completed(tasks)):
        metadata = await task
        
        results.append(metadata)
        progress = (i + 1) / total_urls * 100

        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'Scraping...',
                'progress': round(progress, 2),
                'urls_processed': i + 1,
                'total_urls': total_urls
            }
        )
    logger.info(f"Completed the url scraping part now pushing it to db")

    self.update_state(
        state='PROGRESS',
        meta={
            'status': 'Pushing to DB...',
            'progress': 100,
            'urls_processed': total_urls,
            'total_urls': total_urls
        }
    )
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
        timeout = aiohttp.ClientTimeout(total=30)  
        connector = aiohttp.TCPConnector(limit_per_host=10)  

        async with aiohttp.ClientSession(connector=connector, timeout=timeout, raise_for_status=True) as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30) as response:
                
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

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.warning(f"Failed to scrape {url}: {str(e)}")
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
