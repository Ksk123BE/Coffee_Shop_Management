#-------database_setup.py--------

import sqlite3

DB = "thecafecornner.db"

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    #Menu table 
    cur.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            Item TEXT PRIMARY KEY,
            Price REAL NOT NULL
        )
    """)

    #Insert menu items 
    items = [
        ("Tea", 12),
        ("Vada", 10),
        ("Filter Coffee", 15),
        ("Cappuccino", 50),
        ("Cookies", 20),
        ("Donut", 15),
        ("Puffs", 10),
        ("Cold Coffee", 10),
        ("Mini Samosa (6 pcs)", 20)
    ]
    for item, price in items:
        cur.execute("INSERT OR IGNORE INTO menu (item, price) VALUES (?, ?)", (item, price))

    #Orders table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT,
            iuantity INTEGER,
            price REAL,
            total REAL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized:", DB)

if __name__ == "__main__":
    init_db()

