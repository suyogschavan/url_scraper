# from celery import Celery
# import pandas as pd
# from bs4 import BeautifulSoup
# import requests
# from urllib.parse import urlparse
# from db.connection import get_db_connection
# from dotenv import load_dotenv
# import os

# load_dotenv()

# celery = Celery(__name__, broker=os.getenv("REDIS_URL"))

# @celery.task(bind=True)
# def scrape_urls(self, urls, user_id):
#     conn = get_db_connection()
#     cur = conn.cursor()
#     print("In scrape_urls")
#     for url in urls:
#         print(url)
#         metadata = scrape_metadata(url)
#         print("MetaData:--> ", metadata)
#         if metadata:
#             newUrl = str(metadata["url"])
#             newTitle = str(metadata["title"])
#             newDescription = str(metadata["description"])
#             newKeywords = str(metadata["keywords"])
#             cur.execute(
#                 "INSERT INTO scraped_data (user_id, url, title, description, keywords) VALUES (%s, %s, %s, %s, %s);",
#                 (user_id, newUrl, newTitle, newDescription, newKeywords)
#             )
    
#     conn.commit()
#     cur.close()
#     conn.close()


# def scrape_metadata(url):
#     try:
#         print(url)
        
        
#         response = requests.get(url, timeout=5)

#         if response.status_code != 200:
#             print("cannot access url ", url)
#             return {
#                 "url": url,
#                 "title": "No Title",
#                 "description": "No Description",
#                 "keywords": "No Keywords"
#             }

#         soup = BeautifulSoup(response.text, "html.parser")
#         title = soup.title.string if soup.title else "No Title"
#         description = soup.find("meta", attrs={"name": "description"})
#         keywords = soup.find("meta", attrs={"name": "keywords"})

#         return {
#             "url": url,
#             "title": title,
#             "description": description["content"] if description else "No Description",
#             "keywords": keywords["content"] if keywords else "No Keywords"
#         }
        
#     except Exception as e:
#         print(f"Error scraping {url}: {e}")
#         return {
#             "url": url,
#             "title": "No Title",
#             "description": "No Description",
#             "keywords": "No Keywords"
#         }

# from celery import shared_task

# @shared_task
# def test_celery():
#     return "Celery is working!"


from celery import Celery, shared_task
import aiohttp
import asyncio
import pandas as pd
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from db.connection import get_db_connection
from dotenv import load_dotenv
import os

load_dotenv()

celery = Celery(__name__, broker=os.getenv("REDIS_URL"))

@celery.task(bind=True, max_retries=5, default_retry_delay=60)  # Retry task on failure
def scrape_urls(self, urls, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    print("In scrape_urls")
    
    # Process in batches (reduce DB calls)
    batch_data = []

    # Start the scraping tasks concurrently
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrape_urls_concurrently(urls, user_id, batch_data))
    
    # Perform bulk insert after scraping all URLs
    if batch_data:
        insert_query = """
            INSERT INTO scraped_data (user_id, url, title, description, keywords) 
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.executemany(insert_query, batch_data)
    
    conn.commit()
    cur.close()
    conn.close()
    print("Finished processing all URLs.")

async def scrape_urls_concurrently(urls, user_id, batch_data):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(scrape_metadata(session, url, user_id, batch_data))
        await asyncio.gather(*tasks)

async def scrape_metadata(session, url, user_id, batch_data):
    try:
        print(f"Scraping: {url}")
        async with session.get(url, timeout=5) as response:
            if response.status != 200:
                print(f"Cannot access URL: {url}")
                batch_data.append((user_id, url, "No Title", "No Description", "No Keywords"))
                return

            html = await response.text()
            metadata = extract_metadata(html, url)

            # Append the metadata to batch
            batch_data.append((user_id, metadata["url"], metadata["title"], metadata["description"], metadata["keywords"]))
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        batch_data.append((user_id, url, "No Title", "No Description", "No Keywords"))

def extract_metadata(html, url):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string if soup.title else "No Title"
    description = soup.find("meta", attrs={"name": "description"})
    keywords = soup.find("meta", attrs={"name": "keywords"})

    return {
        "url": url,
        "title": title,
        "description": description["content"] if description else "No Description",
        "keywords": keywords["content"] if keywords else "No Keywords"
    }

@shared_task
def test_celery():
    return "Celery is working!"

