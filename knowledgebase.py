import sqlite3

# Connect to the database
db_path = "database.db"  # Replace with the actual path to your database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query to fetch all rows from the career_knowledge_base table
try:
    cursor.execute("SELECT * FROM career_knowledge_base")
    rows = cursor.fetchall()

    # Print the table contents
    print("Contents of career_knowledge_base table:")
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Error: {e}")
finally:
    conn.close()

