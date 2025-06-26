import sqlite3
from werkzeug.security import generate_password_hash

# Connect to the existing database
conn = sqlite3.connect('data/database.db')
c = conn.cursor()

# Define new user credentials
username = 'admin'
password = generate_password_hash('admin123')  # You can change this

# Insert user
c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
conn.commit()
conn.close()

print("User created successfully.")
