import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _table_columns(conn, table):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(%s)" % table)
    return [r["name"] for r in cur.fetchall()]

def init_items_db():
    """Create normalized schema and migrate old name-based placements/usages if present."""
    conn = get_conn()
    c = conn.cursor()

    # core item types (backwards compatible)
    c.execute('''
    CREATE TABLE IF NOT EXISTS item_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        category TEXT NOT NULL,
        energy_per_min REAL NOT NULL DEFAULT 0.0,
        cost_per_kwh REAL NOT NULL DEFAULT 0.0,
        icon_path TEXT
    )''')

    # categories/map/room/slots
    c.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS maps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        map_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        UNIQUE(map_id, name),
        FOREIGN KEY(map_id) REFERENCES maps(id) ON DELETE CASCADE
    )''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS room_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        slot_index INTEGER NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        UNIQUE(room_id, slot_index),
        FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
    )''')

    conn.commit()

    # If an old placements table exists with map_name/room_name columns, migrate it now.
    existing_tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    if 'placements' in existing_tables:
        cols = _table_columns(conn, 'placements')
        if 'map_name' in cols or 'room_name' in cols:
            # create new placements table using map_id/room_id
            c.execute('''
            CREATE TABLE IF NOT EXISTS placements_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                slot_index INTEGER NOT NULL,
                item_type_id INTEGER,
                on_state INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT,
                FOREIGN KEY(map_id) REFERENCES maps(id) ON DELETE CASCADE,
                FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE,
                FOREIGN KEY(item_type_id) REFERENCES item_types(id) ON DELETE SET NULL
            )''')
            conn.commit()

            # copy rows resolving names -> ids
            rows = c.execute("SELECT map_name, room_name, slot_index, item_type_id, on_state, updated_at FROM placements").fetchall()
            for r in rows:
                mn = r["map_name"] or ""
                rn = r["room_name"] or ""
                mid = add_map_if_not_exists(mn)
                rid = add_room_if_not_exists(mn, rn)
                c.execute('INSERT INTO placements_new (map_id, room_id, slot_index, item_type_id, on_state, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                          (mid, rid, r["slot_index"], r["item_type_id"], r["on_state"], r["updated_at"]))
            conn.commit()
            # preserve old as backup, then replace
            c.execute('ALTER TABLE placements RENAME TO placements_old')
            c.execute('ALTER TABLE placements_new RENAME TO placements')
            conn.commit()

    # daily_item_usage migration (map_name/room_name -> ids)
    if 'daily_item_usage' in existing_tables:
        cols = _table_columns(conn, 'daily_item_usage')
        if 'map_name' in cols or 'room_name' in cols:
            c.execute('''
            CREATE TABLE IF NOT EXISTS daily_item_usage_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day_index INTEGER NOT NULL,
                item_type_id INTEGER,
                energy REAL NOT NULL DEFAULT 0.0,
                cost REAL NOT NULL DEFAULT 0.0,
                map_id INTEGER,
                room_id INTEGER,
                slot_index INTEGER,
                created_at TEXT,
                FOREIGN KEY(item_type_id) REFERENCES item_types(id) ON DELETE SET NULL,
                FOREIGN KEY(map_id) REFERENCES maps(id) ON DELETE SET NULL,
                FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE SET NULL
            )''')
            conn.commit()
            rows = c.execute("SELECT day_index, item_type_id, energy, cost, map_name, room_name, slot_index, created_at FROM daily_item_usage").fetchall()
            for r in rows:
                mn = r["map_name"] or None
                rn = r["room_name"] or None
                mid = add_map_if_not_exists(mn) if mn else None
                rid = add_room_if_not_exists(mn, rn) if (mn and rn) else None
                c.execute('INSERT INTO daily_item_usage_new (day_index, item_type_id, energy, cost, map_id, room_id, slot_index, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (r["day_index"], r["item_type_id"], r["energy"], r["cost"], mid, rid, r["slot_index"], r["created_at"]))
            conn.commit()
            c.execute('ALTER TABLE daily_item_usage RENAME TO daily_item_usage_old')
            c.execute('ALTER TABLE daily_item_usage_new RENAME TO daily_item_usage')
            conn.commit()

    # ensure placements exist (new schema) if none existed previously
    if 'placements' not in existing_tables:
        # fallback: create placements table using ids if somehow missing
        c.execute('''
        CREATE TABLE IF NOT EXISTS placements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            map_id INTEGER NOT NULL,
            room_id INTEGER NOT NULL,
            slot_index INTEGER NOT NULL,
            item_type_id INTEGER,
            on_state INTEGER NOT NULL DEFAULT 0,
            updated_at TEXT,
            FOREIGN KEY(map_id) REFERENCES maps(id) ON DELETE CASCADE,
            FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE,
            FOREIGN KEY(item_type_id) REFERENCES item_types(id) ON DELETE SET NULL
        )''')
        conn.commit()

    conn.close()

# ------------- basic compatibility helpers (unchanged behaviour) -------------
def add_item_type_if_not_exists(name, category, energy_per_min=0.0, cost_per_kwh=0.0, icon_path=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM item_types WHERE name = ?', (name,))
    if c.fetchone():
        conn.close()
        return None
    c.execute('INSERT INTO item_types (name, category, energy_per_min, cost_per_kwh, icon_path) VALUES (?, ?, ?, ?, ?)',
              (name, category, energy_per_min, cost_per_kwh, icon_path))
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

# ------------- normalized helpers (maps/rooms/categories) -------------
def add_category_if_not_exists(name):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM categories WHERE name = ?', (name,))
    r = c.fetchone()
    if r:
        conn.close()
        return r['id']
    c.execute('INSERT INTO categories (name) VALUES (?)', (name,))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return cid

def add_map_if_not_exists(map_name):
    if map_name is None:
        return None
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id FROM maps WHERE name = ?', (map_name,))
    r = c.fetchone()
    if r:
        conn.close()
        return r['id']
    c.execute('INSERT INTO maps (name) VALUES (?)', (map_name,))
    conn.commit()
    mid = c.lastrowid
    conn.close()
    return mid

def add_room_if_not_exists(map_name, room_name):
    if map_name is None or room_name is None:
        return None
    conn = get_conn()
    c = conn.cursor()
    mid = add_map_if_not_exists(map_name)
    c.execute('SELECT id FROM rooms WHERE map_id = ? AND name = ?', (mid, room_name))
    r = c.fetchone()
    if r:
        conn.close()
        return r['id']
    c.execute('INSERT INTO rooms (map_id, name) VALUES (?, ?)', (mid, room_name))
    conn.commit()
    rid = c.lastrowid
    conn.close()
    return rid

def add_room_slot(map_name, room_name, slot_index, slot_name, category):
    conn = get_conn()
    c = conn.cursor()
    room_id = add_room_if_not_exists(map_name, room_name)
    c.execute('SELECT id FROM room_slots WHERE room_id = ? AND slot_index = ?', (room_id, slot_index))
    if c.fetchone():
        conn.close()
        return None
    c.execute('INSERT INTO room_slots (room_id, slot_index, name, category) VALUES (?, ?, ?, ?)',
              (room_id, slot_index, slot_name, category))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid

# ------------- placements (id-based) -------------
def save_placement_by_ids(map_id, room_id, slot_index, item_identifier, on_state=False):
    conn = get_conn()
    c = conn.cursor()
    item_id = None
    if isinstance(item_identifier, int):
        item_id = item_identifier
    elif isinstance(item_identifier, str):
        c.execute('SELECT id FROM item_types WHERE name = ?', (item_identifier,))
        r = c.fetchone()
        if r:
            item_id = r['id']
    updated_at = datetime.utcnow().isoformat()
    c.execute('SELECT id FROM placements WHERE map_id = ? AND room_id = ? AND slot_index = ?', (map_id, room_id, slot_index))
    row = c.fetchone()
    if row:
        c.execute('UPDATE placements SET item_type_id = ?, on_state = ?, updated_at = ? WHERE id = ?',
                  (item_id, 1 if on_state else 0, updated_at, row['id']))
    else:
        c.execute('INSERT INTO placements (map_id, room_id, slot_index, item_type_id, on_state, updated_at) VALUES (?, ?, ?, ?, ?, ?)',
                  (map_id, room_id, slot_index, item_id, 1 if on_state else 0, updated_at))
    conn.commit()
    conn.close()

def save_placement(map_name_or_id, room_name_or_id, slot_index, item_identifier, on_state=False):
    """Backwards-compatible: accept map/room names or ids."""
    if isinstance(map_name_or_id, int):
        map_id = map_name_or_id
    else:
        map_id = add_map_if_not_exists(map_name_or_id)
    if isinstance(room_name_or_id, int):
        room_id = room_name_or_id
    else:
        room_id = add_room_if_not_exists(map_name_or_id, room_name_or_id)
    save_placement_by_ids(map_id, room_id, slot_index, item_identifier, on_state)

def load_placements_for_map(map_name_or_id):
    """Return placements keyed by room name: { room_name: { slot_index: {"item":..., "on":bool} } }"""
    conn = get_conn()
    c = conn.cursor()
    if isinstance(map_name_or_id, int):
        map_id = map_name_or_id
    else:
        map_id = add_map_if_not_exists(map_name_or_id)
    c.execute('''
        SELECT p.room_id, p.slot_index, p.item_type_id, p.on_state, it.name AS item_name, it.category AS item_category, it.energy_per_min, it.cost_per_kwh, r.name AS room_name
        FROM placements p
        JOIN rooms r ON p.room_id = r.id
        LEFT JOIN item_types it ON p.item_type_id = it.id
        WHERE p.map_id = ?
    ''', (map_id,))
    rows = c.fetchall()
    out = {}
    for r in rows:
        room = r['room_name']
        slot = r['slot_index']
        out.setdefault(room, {})
        if r['item_type_id'] is None:
            out[room][slot] = {"item": None, "on": bool(r['on_state'])}
        else:
            out[room][slot] = {"item": {
                "id": r['item_type_id'],
                "name": r['item_name'],
                "category": r['item_category'],
                "energy_per_min": r['energy_per_min'],
                "cost_per_kwh": r['cost_per_kwh']
            }, "on": bool(r['on_state'])}
    conn.close()
    return out

def clear_placements_for_map(map_name_or_id):
    conn = get_conn()
    c = conn.cursor()
    if isinstance(map_name_or_id, int):
        c.execute('DELETE FROM placements WHERE map_id = ?', (map_name_or_id,))
    else:
        mid = add_map_if_not_exists(map_name_or_id)
        c.execute('DELETE FROM placements WHERE map_id = ?', (mid,))
    conn.commit()
    conn.close()

# ------------- daily usage recording (store map_id/room_id) -------------
def record_daily_item_usage(day_index, item_type_id, energy, cost, map_name_or_id=None, room_name_or_id=None, slot_index=None):
    conn = get_conn()
    c = conn.cursor()
    map_id = None
    room_id = None
    if map_name_or_id is not None:
        if isinstance(map_name_or_id, int):
            map_id = map_name_or_id
        else:
            map_id = add_map_if_not_exists(map_name_or_id)
    if room_name_or_id is not None:
        if isinstance(room_name_or_id, int):
            room_id = room_name_or_id
        else:
            room_id = add_room_if_not_exists(map_name_or_id, room_name_or_id)
    created_at = datetime.utcnow().isoformat()
    c.execute('''
        INSERT INTO daily_item_usage (day_index, item_type_id, energy, cost, map_id, room_id, slot_index, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (day_index, item_type_id, energy, cost, map_id, room_id, slot_index, created_at))
    conn.commit()
    conn.close()

def get_daily_usage_for_day(day_index):
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        SELECT diu.*, it.name AS item_name, m.name AS map_name, r.name AS room_name
        FROM daily_item_usage diu
        LEFT JOIN item_types it ON diu.item_type_id = it.id
        LEFT JOIN maps m ON diu.map_id = m.id
        LEFT JOIN rooms r ON diu.room_id = r.id
        WHERE diu.day_index = ?
        ORDER BY energy DESC
    ''', (day_index,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------
# Migration helper (to populate categories table from existing item rows)
# -------------------
def migrate_text_categories_to_categories_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT DISTINCT category FROM item_types')
    for (cat,) in c.fetchall():
        if cat:
            c.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
    conn.commit()
    conn.close()

# Ensure DB schema + migration runs when module is imported
try:
    init_items_db()
except Exception:
    # keep import-safe
    pass