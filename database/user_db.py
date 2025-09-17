# Add sqlite3 for database
import sqlite3
import os


# Database setup
DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')
def init_db():
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute('''CREATE TABLE IF NOT EXISTS users (
		username TEXT PRIMARY KEY,
		password TEXT NOT NULL
	)''')
	conn.commit()
	conn.close()

def register_user(username, password):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	try:
		c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
		conn.commit()
		conn.close()
		return True, ''
	except sqlite3.IntegrityError:
		conn.close()
		return False, 'Username already exists.'

def check_user(username, password):
	conn = sqlite3.connect(DB_PATH)
	c = conn.cursor()
	c.execute('SELECT password FROM users WHERE username=?', (username,))
	row = c.fetchone()
	conn.close()
	if row and row[0] == password:
		return True
	return False