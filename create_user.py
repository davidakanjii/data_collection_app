import sqlite3
from werkzeug.security import generate_password_hash

# Connect to the existing database
conn = sqlite3.connect('data/database.db')
c = conn.cursor()

# Define new user credentials
username = 'admin'
password = generate_password_hash('admin123')  # You can change this
role = 'admin'  # Set role to admin

# Insert user with role
c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))

conn.commit()
conn.close()

print("Admin user created successfully.")
