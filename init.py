import sqlite3

def create_db():
    conn = sqlite3.connect("relay.db")
    cursor = conn.cursor()
    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS relay_status (
            relay_id INTEGER PRIMARY KEY,
            relay_state TEXT NOT NULL
        )
    """)
    # Optionally, insert initial state
    cursor.execute("INSERT OR IGNORE INTO relay_status (relay_id, relay_state) VALUES (1, 'OFF')")
    conn.commit()
    conn.close()
    print("Database and table created successfully.")

if __name__ == "__main__":
    create_db()
