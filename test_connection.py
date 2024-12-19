import sqlite3

try:
    conn = sqlite3.connect("database.db")  # Use the appropriate path if needed
    print("Connected to the database successfully!")
    conn.close()
except sqlite3.Error as e:
    print(f"Error connecting to database: {e}")
