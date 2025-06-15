
# db.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect("dediks.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS dediks (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    email TEXT,
    dedik_id INTEGER,
    duration INTEGER,
    price REAL,
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def get_all_dediks():
    return cur.execute("SELECT id, name, price FROM dediks").fetchall()

def create_order(user_id, email, dedik_id, duration, price):
    cur.execute("""
        INSERT INTO orders (user_id, email, dedik_id, duration, price)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, email, dedik_id, duration, price))
    conn.commit()
    return cur.lastrowid

def mark_order_paid(order_id):
    cur.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))
    conn.commit()

def get_user_orders(user_id):
    return cur.execute("""
        SELECT d.name, o.duration, o.price, o.created_at
        FROM orders o
        JOIN dediks d ON o.dedik_id = d.id
        WHERE o.user_id=?
        ORDER BY o.created_at DESC
    """, (user_id,)).fetchall()
