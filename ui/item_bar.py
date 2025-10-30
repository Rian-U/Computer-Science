import pygame
from ui.button import Button

class ItemBar:
    def __init__(self, screen, font, small_font, categories, height=72, on_category_change=None):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.categories = categories
        self.on_category_change = on_category_change
        self.height = height
        self.rect = pygame.Rect(0, 0, screen.get_width(), self.height)

        # UI state
        self.selected_category = categories[0] if categories else None

        # Create invisible/clickable buttons for categories (we will draw text with alignment ourselves)
        self.category_buttons = []
        padding = 10
        x = padding
        btn_w = (screen.get_width() - padding * (len(categories) + 1)) // max(1, len(categories))
        btn_h = self.height - (padding * 2)
        for cat in categories:
            btn = Button(x, padding, btn_w, btn_h, cat, lambda c=cat: self._select_category(c), font=self.small_font)
            self.category_buttons.append(btn)
            x += btn_w + padding

        # Item area (placeholder) - list of item icons to be drawn to the right
        self.item_placeholders = []
        self._create_placeholders(start_x=x + 20, count=6, size=48, gap=10)

    def _create_placeholders(self, start_x, count, size, gap):
        y = (self.height - size) // 2
        x = start_x
        for _ in range(count):
            r = pygame.Rect(x, y, size, size)
            self.item_placeholders.append((r, None))
            x += size + gap

    def _select_category(self, category):
        self.selected_category = category
        if self.on_category_change:
            self.on_category_change(category)

    def handle_event(self, event):
        # Let invisible/clickable buttons process clicks
        for btn in self.category_buttons:
            btn.handle_event(event)

        # Placeholder example: clicking an item slot could later start drag
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, (rect, item) in enumerate(self.item_placeholders):
                if rect.collidepoint(event.pos):
                    print(f"Item slot {idx} clicked (category={self.selected_category})")
                    break

    def draw(self):
        # Draw bar background
        pygame.draw.rect(self.screen, (40, 40, 40), self.rect)

        # Draw category button backgrounds and aligned texts
        for idx, btn in enumerate(self.category_buttons):
            # background
            pygame.draw.rect(self.screen, (60, 60, 60), btn.rect)
            pygame.draw.rect(self.screen, (100,100,100), btn.rect, 1)

            # render text with smaller font and custom alignment:
            text_surf = self.small_font.render(btn.text, True, (255,255,255))

            if idx == 0:
                # first category: right-aligned inside its button
                text_x = btn.rect.right - 10 - text_surf.get_width()
            elif idx == 1:
                # second category: centered
                text_x = btn.rect.centerx - text_surf.get_width() // 2
            else:
                # last category: right-aligned (as requested)
                text_x = btn.rect.right - 10 - text_surf.get_width()

            text_y = btn.rect.centery - text_surf.get_height() // 2
            self.screen.blit(text_surf, (text_x, text_y))

            # underline selected
            if btn.text == self.selected_category:
                pygame.draw.rect(self.screen, (200, 200, 60), pygame.Rect(btn.rect.x, btn.rect.bottom - 3, btn.rect.w, 3))

        # Draw placeholders (right side)
        for rect, item in self.item_placeholders:
            pygame.draw.rect(self.screen, (60, 60, 60), rect)
            pygame.draw.rect(self.screen, (100, 100, 100), rect, 2)
            if item:
                pygame.draw.circle(self.screen, (0, 160, 200), rect.center, rect.w//3)

    def get_selected_category(self):
        return self.selected_category

    def resize(self, width):
        # Recompute rect width and button widths when window resizes
        self.rect.w = width
        padding = 10
        btn_w = (width - padding * (len(self.categories) + 1)) // max(1, len(self.categories))
        x = padding
        for btn in self.category_buttons:
            btn.rect.x = x
            btn.rect.w = btn_w
            x += btn_w + padding
        # reposition placeholders to the right of the buttons
        start_x = x + 20
        for i, (rect, item) in enumerate(self.item_placeholders):
            rect.x = start_x + i * (rect.w + 10)