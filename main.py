import pygame
import sys

from database.user_db import init_db, register_user, check_user
from ui.input_box import InputBox
from ui.button import Button
from screens.menu_page import MenuPage
from screens.settings_page import SettingsPage
from screens.maps import Map, MAPS, ROOMS, ROOM_SLOTS
from screens.room_page import RoomPage
from ui.item_bar import ItemBar
from database.items_db import init_items_db, add_item_type_if_not_exists, get_items_by_category

pygame.init()

init_db()
init_items_db()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Home Automation Simulation')
clock = pygame.time.Clock()
FONT = pygame.font.SysFont(None, 36)
# smaller font for item bar categories / items
ITEM_SMALL_FONT = pygame.font.SysFont(None, 20)
SMALL_FONT = pygame.font.SysFont(None, 28)

show_fps = False
fullscreen = False
current_map = None
selected_item_category = None
selected_item = None

# ensure map drawn below the item bar
MAP_Y_OFFSET = 72  # same as item_bar height

# add new state for room view
LOGIN, REGISTER, MENU, SETTINGS, SIMULATION, MAP_SELECT, ROOM_VIEW = 'login', 'register', 'menu', 'settings', 'simulation', 'map_select', 'room_view'
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
    # pass MAP_Y_OFFSET so the map and its room rects are shifted down under the item bar
    current_map = Map(screen, MAPS[map_name], ROOMS[map_name], y_offset=MAP_Y_OFFSET)
    screen_state = SIMULATION
    item_bar.resize(screen.get_width())

def add_default_items():
    lighting = [
        ("LED bulbs", "Lighting and Climate Control", 0.005),
        ("Incandescent bulbs", "Lighting and Climate Control", 0.02),
        ("Halogen", "Lighting and Climate Control", 0.018),
        ("Manual Thermostat", "Lighting and Climate Control", 0.001),
        ("Smart Thermostat", "Lighting and Climate Control", 0.002),
        ("Smart plug", "Lighting and Climate Control", 0.0005),
        ("UK plug (Type G)", "Lighting and Climate Control", 0.0),
    ]
    appliances = [
        ("Manual Washing Machine", "Appliances and convenience", 0.12),
        ("Smart Washing Machine", "Appliances and convenience", 0.10),
        ("Conventional oven", "Appliances and convenience", 0.25),
        ("Smart oven", "Appliances and convenience", 0.20),
    ]
    misc = [
        ("Air purifier", "Miscellaneous", 0.04),
        ("Smart Air Purifier", "Miscellaneous", 0.035),
        ("Blinds", "Miscellaneous", 0.0),
        ("Smart Blinds", "Miscellaneous", 0.001),
    ]

    for name, cat, epm in lighting + appliances + misc:
        add_item_type_if_not_exists(name, cat, energy_per_min=epm, cost_per_kwh=0.2, icon_path=None)

add_default_items()

def on_category_change(category):
    global selected_item_category
    selected_item_category = category
    items = get_items_by_category(category)
    print(f"[DEBUG] Category changed -> {category}, loaded {len(items)} items")
    item_bar.set_items(items)

def on_item_selected(item):
    global selected_item
    if item:
        selected_item = item
        print("Item selected:", item["name"])
        globals()["selected_item"] = item

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

item_bar = ItemBar(
    screen, FONT, ITEM_SMALL_FONT,
    categories=["Lighting and Climate Control", "Appliances and convenience", "Miscellaneous"],
    height=96,   # increased to fit categories + items row
    on_category_change=on_category_change,
    on_item_click=on_item_selected
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

# add helper to go back from room view
def go_back_from_room():
    global screen_state, current_room_page
    current_room_page = None
    screen_state = SIMULATION

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
        elif screen_state == SIMULATION:
            # item bar should capture top clicks first
            item_bar.handle_event(event)
            if current_map:
                current_map.handle_event(event)
                # if the map registered a selected room (user clicked a room), open the room view
                selected_room = current_map.get_selected_room()
                if selected_room:
                    # create RoomPage for this room using ROOM_SLOTS if available
                    slots_cfg = ROOM_SLOTS.get(selected_map_name, {}).get(selected_room, [])
                    if not slots_cfg:
                        slots_cfg = [
                            {"name": "Slot 1", "category": "Lighting and Climate Control"},
                            {"name": "Slot 2", "category": "Lighting and Climate Control"},
                        ]
                    # create room page with on_back callback that returns to SIMULATION
                    current_room_page = RoomPage(
                        screen, FONT, SMALL_FONT, selected_map_name, selected_room, slots_cfg,
                        on_back=go_back_from_room
                    )
                    screen_state = ROOM_VIEW
                    # clear selected room on map so it doesn't reopen repeatedly
                    current_map.selected_room = None

        elif screen_state == ROOM_VIEW:
            # let the room handle events first so its Back button has priority,
            # then pass the same event to the item bar so categories/placeholders still work
            if current_room_page:
                current_room_page.handle_event(event)
            item_bar.handle_event(event)

    # draw
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
        if current_map:
            current_map.draw()
        item_bar.draw()
        if selected_item:
            si = SMALL_FONT.render(f"Selected: {selected_item['name']}", True, (200,200,100))
            screen.blit(si, (10, item_bar.rect.bottom + 8))
    elif screen_state == ROOM_VIEW:
        # Draw the room full-screen first (map is not shown here)
        if current_room_page:
            current_room_page.draw()
        # Draw the item bar on top
        item_bar.draw()
        # Ensure Back button is visible above the item bar
        if current_room_page:
            current_room_page.back_button.draw(screen)

    if show_fps:
        fps_text = SMALL_FONT.render(f"FPS: {int(clock.get_fps())}", True, (0,255,0))
        screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()