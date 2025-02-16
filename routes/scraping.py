from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
from db.connection import get_db_connection
from utils.auth_utils import decode_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def scrape_metadata(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None

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
    except:
        return None

@router.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    user_data = decode_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    conn = get_db_connection()
    cur = conn.cursor()
    for url in df["url"]:
        metadata = scrape_metadata(url)
        if metadata:
            cur.execute(
                "INSERT INTO scraped_data (user_id, url, title, description, keywords) VALUES (%s, %s, %s, %s, %s);",
                (user_data["user_id"], metadata["url"], metadata["title"], metadata["description"], metadata["keywords"])
            )

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "Scraping completed!"}
