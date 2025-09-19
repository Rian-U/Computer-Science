import pygame
import sys

from database.user_db import init_db, register_user, check_user
from ui.input_box import InputBox
from ui.button import Button
from screens.menu_page import MenuPage
from screens.settings_page import SettingsPage
from screens.maps import Map, MAPS, ROOMS

pygame.init()

init_db()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Home Automation Simulation')
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
SMALL_FONT = pygame.font.SysFont(None, 28)

show_fps = False
fullscreen = False
current_map = None

LOGIN, REGISTER, MENU, SETTINGS, SIMULATION, MAP_SELECT = 'login', 'register', 'menu', 'settings', 'simulation', 'map_select'
screen_state = LOGIN
selected_map_name = None

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

def go_to_menu():
    global screen_state
    screen_state = MENU

def go_to_simulation():
    go_to_map_select()

def go_to_map_select():
    global screen_state
    screen_state = MAP_SELECT

def select_map(map_name):
    global selected_map_name, screen_state, current_map
    selected_map_name = map_name
    current_map = Map(screen, MAPS[map_name], ROOMS[map_name])
    screen_state = SIMULATION

def go_to_settings():
    global screen_state
    screen_state = SETTINGS

def back_to_menu():
    global screen_state
    screen_state = MENU

def set_show_fps(value):
    global show_fps
    show_fps = value

def set_fullscreen(value):
    global fullscreen, screen
    fullscreen = value
    if fullscreen:
        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))

def logout():
    switch_to_login()

def quit_program():
    pygame.quit()
    sys.exit()
    

menu_page = MenuPage(
    screen, FONT, SMALL_FONT,
    on_start=go_to_simulation,
    on_settings=go_to_settings,
    on_logout=logout,
    on_quit=quit_program,
)

settings_page = SettingsPage(
    screen, FONT, SMALL_FONT,
    show_fps, fullscreen,
    on_back=back_to_menu,
    on_toggle_fps=set_show_fps,
    on_toggle_fullscreen=set_fullscreen
)

def try_login():
    global screen_state, login_error
    if username_box.text and password_box.text:
        if check_user(username_box.text, password_box.text):
            go_to_menu()
        else:
            login_error = 'Incorrect username or password.'
    else:
        login_error = 'Please enter username and password.'

def try_register():
    global screen_state, login_error
    if username_box.text and password_box.text:
        success, msg = register_user(username_box.text, password_box.text)
        if success:
            go_to_menu()
        else:
            login_error = msg
    else:
        login_error = 'Please enter username and password.'

login_button = Button(300, 320, 90, 40, 'Login', try_login, font=FONT)
register_button = Button(410, 320, 90, 40, 'Register', switch_to_register, font=FONT)
register_submit_button = Button(300, 320, 90, 40, 'Register', try_register, font=FONT)
back_button = Button(410, 320, 90, 40, 'Back', switch_to_login, font=FONT)
map_select_buttons = []
def create_map_select_buttons():
    global map_select_buttons
    map_select_buttons = []
    y = 200
    for map_name in MAPS.keys():
        btn = Button(WIDTH//2 - 100, y, 200, 50, map_name, lambda n=map_name: select_map(n), font=FONT)
        map_select_buttons.append(btn)
        y += 70
create_map_select_buttons()

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
        elif screen_state == MENU:
            menu_page.handle_event(event)
        elif screen_state == SETTINGS:
            settings_page.handle_event(event)
        elif screen_state == MAP_SELECT:
            for btn in map_select_buttons:
                btn.handle_event(event)
        elif screen_state == SIMULATION and current_map:
            current_map.handle_event(event)

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
    elif screen_state == MENU:
        menu_page.draw()
    elif screen_state == SETTINGS:
        settings_page.draw()
    elif screen_state == MAP_SELECT:
        screen.fill((30, 30, 30))
        title = FONT.render("Select a Map", True, (255,255,255))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for btn in map_select_buttons:
            btn.draw(screen)
    elif screen_state == SIMULATION:
        sim_title = FONT.render('Simulation Running...', True, (255,255,255))
        screen.blit(sim_title, (WIDTH//2 - sim_title.get_width()//2, HEIGHT//2 - 20))
        if current_map:
            current_map.draw()

    if show_fps:
        fps_text = SMALL_FONT.render(f"FPS: {int(clock.get_fps())}", True, (0,255,0))
        screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()