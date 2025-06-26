import sqlite3

conn = sqlite3.connect('data/database.db')
cursor = conn.cursor()

# Add 'role' column with default 'user' for existing users
try:
    cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
    print("Role column added successfully.")
except sqlite3.OperationalError as e:
    print("Column might already exist:", e)

conn.commit()
conn.close()
