import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_items_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS item_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        energy_per_min REAL NOT NULL DEFAULT 0.0,
        cost_per_kwh REAL NOT NULL DEFAULT 0.0,
        icon_path TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_item_type_if_not_exists(name, category, energy_per_min=0.0, cost_per_kwh=0.0, icon_path=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM item_types WHERE name = ?', (name,))
    if c.fetchone():
        conn.close()
        return None
    c.execute('''
        INSERT INTO item_types (name, category, energy_per_min, cost_per_kwh, icon_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, category, energy_per_min, cost_per_kwh, icon_path))
    conn.commit()
    item_id = c.lastrowid
    conn.close()
    return item_id

def get_items_by_category(category):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM item_types WHERE category = ? ORDER BY name', (category,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_items():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM item_types ORDER BY category, name')
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]
