import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')
if not os.path.exists(DB):
    print("DB not found at", DB); raise SystemExit(1)
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT category, COUNT(*) FROM item_types GROUP BY category ORDER BY COUNT(*) DESC")
for cat, cnt in cur.fetchall():
    print(f"{cat!r}: {cnt}")
print("\nAll items (name → category):")
cur.execute("SELECT name, category FROM item_types ORDER BY category, name")
for name, cat in cur.fetchall():
    print(f"{name!r} -> {cat!r}")
conn.close()