import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')
if not os.path.exists(DB):
    print("DB file not found:", DB); raise SystemExit(1)
conn = sqlite3.connect(DB)
cur = conn.cursor()

# list tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("Tables:", tables)

for t in tables:
    print("\nSchema for table:", t)
    cur.execute(f"PRAGMA table_info({t})")
    for cid, name, typ, notnull, dflt, pk in cur.fetchall():
        print(f"  {name} {typ}  NOTNULL={notnull}  PK={pk}  DEFAULT={dflt}")
    try:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        print("  Rows:", cur.fetchone()[0])
    except Exception as e:
        print("  (could not count rows)", e)

# show sample rows for common tables
for t in ('item_types','users'):
    if t in tables:
        print(f"\nSample rows from {t}:")
        cur.execute(f"SELECT * FROM {t} LIMIT 10")
        for r in cur.fetchall():
            print(" ", r)

conn.close()