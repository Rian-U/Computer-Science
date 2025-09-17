import pygame
import sys

from database.user_db import init_db, register_user, check_user
from ui.input_box import InputBox
from ui.button import Button

pygame.init()

init_db()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Home Automation Simulation')
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 28)

LOGIN, REGISTER, SIMULATION = 'login', 'register', 'simulation'
screen_state = LOGIN

# Input boxes for login/register
username_box = InputBox(300, 200, 200, 40, font=FONT)
password_box = InputBox(300, 260, 200, 40, font=FONT)
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

login_button = Button(300, 320, 90, 40, 'Login', try_login, font=FONT)
register_button = Button(410, 320, 90, 40, 'Register', switch_to_register, font=FONT)
register_submit_button = Button(300, 320, 90, 40, 'Register', try_register, font=FONT)
back_button = Button(410, 320, 90, 40, 'Back', switch_to_login, font=FONT)

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
        sim_title = FONT.render('Simulation Running...', True, (255,255,255))
        screen.blit(sim_title, (WIDTH//2 - sim_title.get_width()//2, HEIGHT//2 - 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

def test():
    pass