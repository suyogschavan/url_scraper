from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor  # To get data as a dictionary
from pydantic import BaseModel
from typing import List

# FastAPI instance
app = FastAPI()

# PostgreSQL Connection
DB_URL = "postgres://avnadmin:AVNS_vr11EDEzCcJfqx2PGIg@url-scraper-assignment-suyogschavan03-3b00.h.aivencloud.com:21361/defaultdb?sslmode=require"

def get_db_connection():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)  # Returns data as dictionary

# User Model for Request Body
class User(BaseModel):
    name: str
    age: int

# ✅ 1. Create Table (Run at startup)
@app.on_event("startup")
def create_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            age INT
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

# ✅ 2. Get All Users
@app.get("/users", response_model=List[dict])
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

# ✅ 3. Get User by ID
@app.get("/users/{user_id}", response_model=dict)
def get_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# ✅ 4. Create a New User
@app.post("/users", response_model=dict)
def create_user(user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, age) VALUES (%s, %s) RETURNING *;",
        (user.name, user.age)
    )
    new_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_user

# ✅ 5. Update a User
@app.put("/users/{user_id}", response_model=dict)
def update_user(user_id: int, user: User):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET name = %s, age = %s WHERE id = %s RETURNING *;",
        (user.name, user.age, user_id)
    )
    updated_user = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return updated_user

# ✅ 6. Delete a User
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s RETURNING id;", (user_id,))
    deleted_id = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted_id is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User with ID {deleted_id['id']} deleted successfully"}

