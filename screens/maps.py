import pygame

MAPS = {
    "Map 1": "assets/map1_bg.png",
    "Map 2": "assets/map2_bg.png",
    "Map 3": "assets/map3_bg.jpg"
}

ROOMS = {
    "Map 1": {
        "bedroom": pygame.Rect(175, 175, 175, 110),
        "bathroom": pygame.Rect(150, 350, 100, 110),
        "office": pygame.Rect(340, 200, 140, 100),
        "living_room": pygame.Rect(480, 350, 150, 110),
        "kitchen": pygame.Rect(375, 350, 100, 110),
        "bedroom2": pygame.Rect(480, 190, 200, 110),
    },
    "Map 2": {
        "bedroom": pygame.Rect(60, 60, 180, 100),
        "bathroom": pygame.Rect(260, 60, 180, 100),
        "office": pygame.Rect(460, 60, 180, 100),
        "living_room": pygame.Rect(60, 180, 180, 100),
        "dining": pygame.Rect(260, 180, 180, 100),
        "kitchen": pygame.Rect(460, 180, 180, 100),
    },
    "Map 3": {
        "bedroom": pygame.Rect(80, 80, 160, 90),
        "bathroom": pygame.Rect(260, 80, 160, 90),
        "office": pygame.Rect(440, 80, 160, 90),
        "living_room": pygame.Rect(80, 190, 160, 90),
        "dining": pygame.Rect(260, 190, 160, 90),
        "kitchen": pygame.Rect(440, 190, 160, 90),
    }
}

# per-room slot configuration (categories normalized to code/DB)
ROOM_SLOTS = {
    "Map 1": {
        "bedroom": [
            {"name": "Ceiling Light", "category": "ElectricsAndThermo"},
            {"name": "Thermostat", "category": "ElectricsAndThermo"},
            {"name": "Side Plug", "category": "ElectricsAndThermo"},
        ],
        "bedroom2": [
            {"name": "Ceiling Light", "category": "ElectricsAndThermo"},
            {"name": "Blinds", "category": "Miscellaneous"},
        ],
        "bathroom": [
            {"name": "Vanity Light", "category": "ElectricsAndThermo"},
            {"name": "Plug", "category": "ElectricsAndThermo"},
        ],
        "office": [
            {"name": "Desk Light", "category": "ElectricsAndThermo"},
            {"name": "Smart Plug", "category": "ElectricsAndThermo"},
            {"name": "Air Purifier Slot", "category": "Miscellaneous"},
        ],
        "living_room": [
            {"name": "Main Light", "category": "ElectricsAndThermo"},
            {"name": "TV Plug", "category": "Appliances"},
            {"name": "Blinds", "category": "Miscellaneous"},
        ],
        "kitchen": [
            {"name": "Ceiling Light", "category": "ElectricsAndThermo"},
            {"name": "Oven Slot", "category": "Appliances"},
            {"name": "Washing Machine Slot", "category": "Appliances"},
        ],
    },
    "Map 2": {
        "bedroom": [
            {"name": "Light", "category": "ElectricsAndThermo"},
            {"name": "Blinds", "category": "Miscellaneous"},
        ],
        "bathroom": [
            {"name": "Light", "category": "ElectricsAndThermo"}
        ],
        "office": [
            {"name": "Desk Plug", "category": "ElectricsAndThermo"},
            {"name": "Air Purifier Slot", "category": "Miscellaneous"},
        ],
        "living_room": [
            {"name": "Main Light", "category": "ElectricsAndThermo"},
            {"name": "Oven Slot", "category": "Appliances"},
        ],
        "dining": [
            {"name": "Light", "category": "ElectricsAndThermo"},
            {"name": "Blinds", "category": "Miscellaneous"},
        ],
        "kitchen": [
            {"name": "Main Light", "category": "ElectricsAndThermo"},
            {"name": "Oven Slot", "category": "Appliances"},
        ],
    },
    "Map 3": {
        "bedroom": [
            {"name": "Light", "category": "ElectricsAndThermo"},
            {"name": "Thermostat", "category": "ElectricsAndThermo"},
        ],
        "bathroom": [
            {"name": "Light", "category": "ElectricsAndThermo"}
        ],
        "office": [
            {"name": "Desk Light", "category": "ElectricsAndThermo"},
            {"name": "Smart Plug", "category": "ElectricsAndThermo"},
        ],
        "living_room": [
            {"name": "Main Light", "category": "ElectricsAndThermo"},
            {"name": "Blinds", "category": "Miscellaneous"},
            {"name": "TV Plug", "category": "Appliances"},
        ],
        "dining": [
            {"name": "Light", "category": "ElectricsAndThermo"}
        ],
        "kitchen": [
            {"name": "Main Light", "category": "ElectricsAndThermo"},
            {"name": "Oven Slot", "category": "Appliances"},
        ],
    }
}

class Map:
    def __init__(self, screen, bg_path, rooms, y_offset=100):
        self.screen = screen
        self.y_offset = y_offset

        loaded = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(loaded, (screen.get_width(), screen.get_height() - self.y_offset))
        self.bg_rect = self.bg.get_rect(topleft=(0, self.y_offset))

        self.rooms = {name: rect.copy().move(0, self.y_offset) for name, rect in rooms.items()}

        self.selected_room = None
        self.hovered_room = None
        self.room_items = {name: None for name in self.rooms}

    def draw(self):
        self.screen.blit(self.bg, self.bg_rect.topleft)
        for name, rect in self.rooms.items():
            if name == self.selected_room:
                pygame.draw.rect(self.screen, (0, 200, 0), rect, 3)
            elif name == self.hovered_room:
                pygame.draw.rect(self.screen, (200, 100, 0), rect, 3)
            item = self.room_items.get(name)
            if item:
                pygame.draw.circle(self.screen, (0, 0, 255), rect.center, min(rect.w, rect.h)//6)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered_room = None
            for name, rect in self.rooms.items():
                if rect.collidepoint(event.pos):
                    self.hovered_room = name
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.selected_room = None
            for name, rect in self.rooms.items():
                if rect.collidepoint(event.pos):
                    self.selected_room = name
                    print(f"Selected room: {name}")
                    break

    def place_item_in_room(self, room_name, item):
        if room_name in self.room_items:
            self.room_items[room_name] = item

    def get_selected_room(self):
        return self.selected_room
