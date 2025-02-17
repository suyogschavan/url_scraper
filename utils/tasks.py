from celery import Celery
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from db.connection import get_db_connection
from dotenv import load_dotenv
import os

load_dotenv()

celery = Celery(__name__, broker=os.getenv("REDIS_URL"))

@celery.task(bind=True)
def scrape_urls(self, urls, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    print("In scrape_urls")
    for url in urls:
        print(url)
        metadata = scrape_metadata(url)
        print("MetaData:--> ", metadata)
        if metadata:
            newUrl = str(metadata["url"])
            newTitle = str(metadata["title"])
            newDescription = str(metadata["description"])
            newKeywords = str(metadata["keywords"])
            cur.execute(
                "INSERT INTO scraped_data (user_id, url, title, description, keywords) VALUES (%s, %s, %s, %s, %s);",
                (user_id, newUrl, newTitle, newDescription, newKeywords)
            )
    
    conn.commit()
    cur.close()
    conn.close()


def scrape_metadata(url):
    try:
        print(url)
        
        
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            print("cannot access url ", url)
            return {
                "url": url,
                "title": "No Title",
                "description": "No Description",
                "keywords": "No Keywords"
            }

        soup = BeautifulSoup(response.text, "html.parser")
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
        print(f"Error scraping {url}: {e}")
        return {
            "url": url,
            "title": "No Title",
            "description": "No Description",
            "keywords": "No Keywords"
        }
