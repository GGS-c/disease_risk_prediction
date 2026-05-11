import sqlite3
import os

db_path = os.path.join('instance', 'disease_prediction.db')
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN city VARCHAR(50);")
        conn.commit()
        print("Column 'city' added successfully.")
    except Exception as e:
        print("Notice/Error:", e)
    finally:
        conn.close()
else:
    print(f"Database {db_path} not found.")
