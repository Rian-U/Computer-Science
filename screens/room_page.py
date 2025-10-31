import os
import pygame
from ui.button import Button

class RoomPage:
    def __init__(self, screen, font, small_font, map_name, room_name, slots_config, on_back, room_image_path=None):
        """
        Full-window room view. Slots start empty. room_image_path optional (scaled to fit).
        slots_config: list of {"name": str, "category": str}
        """
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.map_name = map_name
        self.room_name = room_name
        self.on_back = on_back
        self.room_image_path = room_image_path

        # create slots (empty)
        self.slots = []
        for s in slots_config:
            self.slots.append({
                "name": s.get("name", ""),
                "category": s.get("category", ""),
                "item": None
            })

        # UI geometry
        w, h = screen.get_size()
        self.title_y = 24
        self.top_padding = 12
        self.slot_size = 96
        self.slot_gap = 24
        self.slot_top = 120

        # back button (moved lower so it doesn't overlap item bar / categories)
        # place the Back button below the item bar (default item bar height is 96)
        self.back_button = Button(16, 104, 90, 36, "Back", self._on_back, font=self.font)

        # load room image if available
        if not self.room_image_path:
            candidate1 = os.path.join("assets", "rooms", f"{self.map_name}_{self.room_name}.png")
            candidate2 = os.path.join("assets", "rooms", f"{self.room_name}.png")
            if os.path.exists(candidate1):
                self.room_image_path = candidate1
            elif os.path.exists(candidate2):
                self.room_image_path = candidate2
            else:
                self.room_image_path = None

        self._load_background()

    def _load_background(self):
        self.bg_surf = None
        if self.room_image_path:
            try:
                surf = pygame.image.load(self.room_image_path).convert_alpha()
                self.bg_surf = pygame.transform.smoothscale(surf, self.screen.get_size())
            except Exception:
                self.bg_surf = None

    def _on_back(self):
        if callable(self.on_back):
            self.on_back()

    def handle_event(self, event):
        # back button
        self.back_button.handle_event(event)

        # For now: slots do not accept placement by clicking.
        # Clicking a slot prints info for future drag/drop implementation.
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, slot in enumerate(self.slots):
                rect = self._slot_rect(idx)
                if rect.collidepoint(event.pos):
                    # if a selected_item exists, inform user placement is not implemented yet
                    selected_item = globals().get("selected_item")
                    if selected_item:
                        print(f"[ROOM] clicked slot '{slot['name']}' (requires {slot['category']}) - placement not implemented yet")
                    else:
                        print(f"[ROOM] clicked slot '{slot['name']}' (allowed category: {slot['category']}) - no placement yet")
                    break

    def draw(self):
        # Full-screen room view (map is NOT drawn behind)
        if self.bg_surf:
            self.screen.blit(self.bg_surf, (0, 0))
        else:
            self.screen.fill((28, 28, 30))
            pygame.draw.rect(self.screen, (36, 36, 40), (0, 0, 84, self.screen.get_width()))

        # Title
        title_surf = self.font.render(self.room_name, True, (245,245,245))
        self.screen.blit(title_surf, (self.screen.get_width()//2 - title_surf.get_width()//2, self.title_y))

        # Draw slots centered horizontally
        count = len(self.slots)
        total_width = count * self.slot_size + (count - 1) * self.slot_gap
        start_x = max(20, self.screen.get_width()//2 - total_width//2)
        for idx, slot in enumerate(self.slots):
            rect = pygame.Rect(start_x + idx * (self.slot_size + self.slot_gap), self.slot_top, self.slot_size, self.slot_size)
            pygame.draw.rect(self.screen, (70,70,70), rect)
            pygame.draw.rect(self.screen, (140,140,140), rect, 2)

            # draw category tag (fit to width)
            cat_surf = self._render_text_fit(slot["category"], rect.w - 12, bold=True)
            self.screen.blit(cat_surf, (rect.x + 6, rect.y + 6))

            # draw slot name below category (fit)
            name_surf = self._render_text_fit(slot["name"], rect.w - 12)
            # place it under the category line with small spacing
            self.screen.blit(name_surf, (rect.x + 6, rect.y + 6 + cat_surf.get_height() + 2))

            # item placeholder area (empty for now)
            ph_rect = pygame.Rect(rect.x + 8, rect.y + rect.h//2 - 12, rect.w - 16, 24)
            pygame.draw.rect(self.screen, (50,50,50), ph_rect)
            pygame.draw.rect(self.screen, (100,100,100), ph_rect, 1)

        # Draw back button on top
        self.back_button.draw(self.screen)

    def _slot_rect(self, idx):
        total_width = len(self.slots) * self.slot_size + (len(self.slots)-1) * self.slot_gap
        start_x = max(20, self.screen.get_width()//2 - total_width//2)
        x = start_x + idx * (self.slot_size + self.slot_gap)
        return pygame.Rect(x, self.slot_top, self.slot_size, self.slot_size)

    def _render_text_fit(self, text, max_w, bold=False):
        """Return a Surface with text rendered small enough to fit inside max_w.
           Tries decreasing font sizes then truncates with ellipsis if needed."""
        # prefer smaller sizes so text fits
        for size in (20, 18, 16, 14, 12, 10, 8):
            f = pygame.font.SysFont(None, size, bold=bold)
            w, h = f.size(text)
            if w <= max_w:
                return f.render(text, True, (230,230,230))
        # truncate if necessary
        f = pygame.font.SysFont(None, 8, bold=bold)
        txt = text
        while txt and f.size(txt + '…')[0] > max_w:
            txt = txt[:-1]
        return f.render((txt + '…') if txt else '…', True, (230,230,230))

    def get_slot_config(self):
        return [(s["name"], s["category"]) for s in self.slots]