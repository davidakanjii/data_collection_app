import sqlite3

conn = sqlite3.connect('data/database.db')
c = conn.cursor()

try:
    c.execute("ALTER TABLE submissions ADD COLUMN timestamp TEXT")
    print("Timestamp column added successfully.")
except:
    print("Timestamp column may already exist.")

conn.commit()
conn.close()
