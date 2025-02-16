from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from db.connection import get_db_connection
from utils.auth_utils import decode_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.get('/urls')
def getUrls(token:str=Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(401, detail="Invalid token" )
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scraped_data WHERE user_id=%s", (user['user_id'], ))
    result = cur.fetchall()
    return result
    