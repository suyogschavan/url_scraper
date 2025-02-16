from db.connection import get_db_connection

def create_scraped_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
                CREATE TABLE IF NOT EXISTS scraped_data(
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    url TEXT,
                    title TEXT,
                    description TEXT,
                    keywords TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                ''')
    conn.commit()
    cur.close()
    conn.close()