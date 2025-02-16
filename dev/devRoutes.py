from fastapi import HTTPException, APIRouter
from db.connection import get_db_connection

router = APIRouter()

@router.get("/dev/getUsers")
def getUsers():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

@router.get("/dev/getScrapedData")
def getScrapedData():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scraped_data;")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data