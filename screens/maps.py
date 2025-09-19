import pygame

MAPS = {
    "Map 1": "assets/map1_bg.png",
    "Map 2": "assets/map2_bg.png",
    "Map 3": "assets/map3_bg.jpg"
}

ROOMS = {
    "Map 1": {
        "bedroom": pygame.Rect(40, 40, 200, 110),
        "bathroom": pygame.Rect(260, 40, 200, 110),
        "office": pygame.Rect(480, 40, 200, 110),
        "living_room": pygame.Rect(40, 190, 200, 110),
        "dining": pygame.Rect(260, 190, 200, 110),
        "kitchen": pygame.Rect(480, 190, 200, 110),
    },
    "Map 2": {
        # Example: adjust these for Map 2's layout
        "bedroom": pygame.Rect(60, 60, 180, 100),
        "bathroom": pygame.Rect(260, 60, 180, 100),
        "office": pygame.Rect(460, 60, 180, 100),
        "living_room": pygame.Rect(60, 180, 180, 100),
        "dining": pygame.Rect(260, 180, 180, 100),
        "kitchen": pygame.Rect(460, 180, 180, 100),
    },
    "Map 3": {
        # Example: adjust these for Map 3's layout
        "bedroom": pygame.Rect(80, 80, 160, 90),
        "bathroom": pygame.Rect(260, 80, 160, 90),
        "office": pygame.Rect(440, 80, 160, 90),
        "living_room": pygame.Rect(80, 190, 160, 90),
        "dining": pygame.Rect(260, 190, 160, 90),
        "kitchen": pygame.Rect(440, 190, 160, 90),
    }
}

class Map:
    def __init__(self, screen, bg_path, rooms):
        self.screen = screen
        self.bg = pygame.image.load(bg_path).convert()
        self.bg = pygame.transform.scale(self.bg, (screen.get_width(), screen.get_height()))
        self.rooms = rooms
        self.selected_room = None
        self.hovered_room = None
        self.room_items = {name: None for name in self.rooms}

    def draw(self):
        self.screen.blit(self.bg, (0, 0))
        for name, rect in self.rooms.items():
            color = (0, 255, 0) if name == self.selected_room else (255, 0, 0) if name == self.hovered_room else (0, 0, 0, 0)
            if name == self.selected_room or name == self.hovered_room:
                pygame.draw.rect(self.screen, color, rect, 3)
            item = self.room_items[name]
            if item:
                pygame.draw.circle(self.screen, (0, 0, 255), rect.center, 15)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered_room = None
            for name, rect in self.rooms.items():
                if rect.collidepoint(event.pos):
                    self.hovered_room = name
                    break
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.selected_room = None
            for name, rect in self.rooms.items():
                if rect.collidepoint(event.pos):
                    self.selected_room = name
                    print(f"{name} clicked")
                    break

    def place_item_in_room(self, room_name, item):
        if room_name in self.room_items:
            self.room_items[room_name] = item

    def get_selected_room(self):
        return self.selected_room