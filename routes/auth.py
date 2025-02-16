from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from db.connection import get_db_connection
from utils.hashing import hash_password, verify_password
from utils.auth_utils import create_token
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register")
def register_user(user: UserRegister):
    conn = get_db_connection()
    cur = conn.cursor()
    hashed_pw = hash_password(user.password)
    
    try:
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s);",
            (user.username, user.email, hashed_pw)
        )
        cur.execute("SELECT id FROM users WHERE email = %s;", (user.email,))
        user_id = cur.fetchone()["id"]
        conn.commit()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail="User already exists")
    
    cur.close()
    conn.close()
    
    return {"message": "User registered successfully", "token": create_token(user_id)}

@router.post("/login")
def login_user(user: UserLogin):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s;", (user.email,))
    user_data = cur.fetchone()
    cur.close()
    conn.close()

    if not user_data or not verify_password(user.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"message": "Login successful", "token": create_token(user_data["id"])}



def authenticate_user(username: str, password: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_token(user["id"])
    return {"access_token": access_token, "token_type": "bearer"}
