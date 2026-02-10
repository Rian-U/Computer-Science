import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'simulation.db')
conn = sqlite3.connect(DB)
cur = conn.cursor()
# map old->new
cur.execute("UPDATE item_types SET category = ? WHERE category = ?", ('ElectricsAndThermo', 'Lighting and Climate Control'))
cur.execute("UPDATE item_types SET category = ? WHERE category = ?", ('ElectricsAndThermo', 'Electrics&Thermo'))
cur.execute("UPDATE item_types SET category = ? WHERE category = ?", ('Appliances', 'Appliances and convenience'))
conn.commit()
print("Migration applied.")
conn.close()