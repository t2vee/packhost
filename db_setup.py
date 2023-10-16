import sqlite3


# Create a table to store access logs
db_connection = sqlite3.connect("access_logs.db")

# Create a table to store upload and download counters
db_connection.execute('''
    CREATE TABLE IF NOT EXISTS counters (
        id INTEGER PRIMARY KEY,
        uploads INTEGER DEFAULT 0,
        downloads INTEGER DEFAULT 0
    )
''')
db_connection.commit()
