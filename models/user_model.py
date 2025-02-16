from db.connection import get_db_connection

def create_user_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")
    cur.execute('''
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL, 
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );
                ''')
    conn.commit()
    cur.close()
    conn.close()