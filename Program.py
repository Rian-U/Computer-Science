# Basic Pygame Simulation Template with Login/Register
import pygame
import sys

# Add sqlite3 for database
import sqlite3
import os

pygame.init()

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

init_db()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Home Automation Simulation')
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 28)

# Input box class
class InputBox:
	def __init__(self, x, y, w, h, text=''):
		self.rect = pygame.Rect(x, y, w, h)
		self.color = pygame.Color('lightskyblue3')
		self.text = text
		self.txt_surface = FONT.render(text, True, (255,255,255))
		self.active = False

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			# Toggle active state if clicked
			if self.rect.collidepoint(event.pos):
				self.active = not self.active
			else:
				self.active = False
			self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')
		if event.type == pygame.KEYDOWN:
			if self.active:
				if event.key == pygame.K_RETURN:
					pass  # Do nothing on enter
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
				self.txt_surface = FONT.render(self.text, True, (255,255,255))

	def draw(self, screen):
		# Blit the text
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
		# Blit the rect
		pygame.draw.rect(screen, self.color, self.rect, 2)

# Button class
class Button:
	def __init__(self, x, y, w, h, text, callback):
		self.rect = pygame.Rect(x, y, w, h)
		self.text = text
		self.callback = callback
		self.color = pygame.Color('gray15')
		self.txt_surface = FONT.render(text, True, (255,255,255))

	def handle_event(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			if self.rect.collidepoint(event.pos):
				self.callback()

	def draw(self, screen):
		pygame.draw.rect(screen, self.color, self.rect)
		screen.blit(self.txt_surface, (self.rect.x+10, self.rect.y+10))

LOGIN, REGISTER, SIMULATION = 'login', 'register', 'simulation'
screen_state = LOGIN

# Input boxes for login/register
username_box = InputBox(300, 200, 200, 40)
password_box = InputBox(300, 260, 200, 40)
input_boxes = [username_box, password_box]

login_error = ''

def switch_to_register():
	global screen_state, username_box, password_box, login_error
	screen_state = REGISTER
	username_box.text = ''
	password_box.text = ''
	username_box.txt_surface = FONT.render('', True, (255,255,255))
	password_box.txt_surface = FONT.render('', True, (255,255,255))
	login_error = ''

def switch_to_login():
	global screen_state, username_box, password_box, login_error
	screen_state = LOGIN
	username_box.text = ''
	password_box.text = ''
	username_box.txt_surface = FONT.render('', True, (255,255,255))
	password_box.txt_surface = FONT.render('', True, (255,255,255))
	login_error = ''

def try_login():
	global screen_state, login_error
	if username_box.text and password_box.text:
		if check_user(username_box.text, password_box.text):
			screen_state = SIMULATION
		else:
			login_error = 'Incorrect username or password.'
	else:
		login_error = 'Please enter username and password.'

def try_register():
	global screen_state, login_error
	if username_box.text and password_box.text:
		success, msg = register_user(username_box.text, password_box.text)
		if success:
			screen_state = SIMULATION
		else:
			login_error = msg
	else:
		login_error = 'Please enter username and password.'
login_button = Button(300, 320, 90, 40, 'Login', try_login)
register_button = Button(410, 320, 90, 40, 'Register', switch_to_register)
register_submit_button = Button(300, 320, 90, 40, 'Register', try_register)
back_button = Button(410, 320, 90, 40, 'Back', switch_to_login)

running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		if screen_state in [LOGIN, REGISTER]:
			for box in input_boxes:
				box.handle_event(event)
			if screen_state == LOGIN:
				login_button.handle_event(event)
				register_button.handle_event(event)
			else:
				register_submit_button.handle_event(event)
				back_button.handle_event(event)

	screen.fill((30, 30, 30))

	if screen_state == LOGIN:
		title = FONT.render('Login', True, (255,255,255))
		screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
		user_label = SMALL_FONT.render('Username:', True, (200,200,200))
		pass_label = SMALL_FONT.render('Password:', True, (200,200,200))
		screen.blit(user_label, (200, 210))
		screen.blit(pass_label, (200, 270))
		for box in input_boxes:
			box.draw(screen)
		login_button.draw(screen)
		register_button.draw(screen)
		if login_error:
			err = SMALL_FONT.render(login_error, True, (255, 80, 80))
			screen.blit(err, (300, 370))
	elif screen_state == REGISTER:
		title = FONT.render('Register', True, (255,255,255))
		screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
		user_label = SMALL_FONT.render('Username:', True, (200,200,200))
		pass_label = SMALL_FONT.render('Password:', True, (200,200,200))
		screen.blit(user_label, (200, 210))
		screen.blit(pass_label, (200, 270))
		for box in input_boxes:
			box.draw(screen)
		register_submit_button.draw(screen)
		back_button.draw(screen)
		if login_error:
			err = SMALL_FONT.render(login_error, True, (255, 80, 80))
			screen.blit(err, (300, 370))
	elif screen_state == SIMULATION:
		# --- Draw your simulation objects here ---
		sim_title = FONT.render('Simulation Running...', True, (255,255,255))
		screen.blit(sim_title, (WIDTH//2 - sim_title.get_width()//2, HEIGHT//2 - 20))

	pygame.display.flip()
	clock.tick(60)

pygame.quit()
sys.exit()
