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

class Map:
    def __init__(self, screen, bg_path, rooms, y_offset=100):
        """
        screen: pygame display surface
        bg_path: path to background image
        rooms: dict of room_name -> pygame.Rect (coordinates relative to top-left of the image)
        y_offset: number of pixels to move the map down (and shift the room rects the same amount)
        """
        self.screen = screen
        self.y_offset = y_offset

        loaded = pygame.image.load(bg_path).convert()
        # scale background to fit width and remaining height (so map appears lower)
        self.bg = pygame.transform.scale(loaded, (screen.get_width(), screen.get_height() - self.y_offset))
        self.bg_rect = self.bg.get_rect(topleft=(0, self.y_offset))

        # shift room rects by y_offset so they align with the moved background
        self.rooms = {name: rect.copy().move(0, self.y_offset) for name, rect in rooms.items()}

        self.selected_room = None
        self.hovered_room = None
        self.room_items = {name: None for name in self.rooms}

    def draw(self):
        # draw background at offset
        self.screen.blit(self.bg, self.bg_rect.topleft)

        # draw hover/selection rectangles and any items
        for name, rect in self.rooms.items():
            if name == self.selected_room:
                pygame.draw.rect(self.screen, (0, 200, 0), rect, 3)
            elif name == self.hovered_room:
                pygame.draw.rect(self.screen, (200, 100, 0), rect, 3)
            # draw item placeholder if present
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