import sqlite3
import os
import re
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')

if not os.path.exists(DB):
    print("DB not found at", DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT id, name FROM item_types")
rows = cur.fetchall()

groups = {}
for id_, name in rows:
    key = re.sub(r'[^A-Za-z0-9]', '', name).lower()   # normalize (remove punctuation/spaces)
    groups.setdefault(key, []).append((id_, name))

to_delete = []
for key, items in groups.items():
    hyphen_items = [it for it in items if '-' in it[1]]
    if hyphen_items:
        # keep hyphen variant(s), delete non-hyphen duplicates
        for it in items:
            if '-' not in it[1]:
                to_delete.append(it[0])

if to_delete:
    cur.executemany("DELETE FROM item_types WHERE id = ?", [(i,) for i in to_delete])
    conn.commit()
    print(f"Deleted {len(to_delete)} duplicate item rows (kept hyphen variants).")
else:
    print("No duplicates found.")

conn.close()