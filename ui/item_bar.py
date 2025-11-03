import os
import pygame
from ui.button import Button

class ItemBar:
    def __init__(self, screen, font, small_font, categories, height=96, on_category_change=None, on_item_click=None, placeholder_size=72, placeholder_gap=10):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.categories = categories
        self.on_category_change = on_category_change
        self.on_item_click = on_item_click

        # bar height allows category row + optional item row
        self.height = height
        self.rect = pygame.Rect(0, 0, screen.get_width(), self.height)

        # placeholder layout config (increased size so labels can be larger)
        self.placeholder_size = placeholder_size
        self.placeholder_gap = placeholder_gap

        # item label font (larger so text is readable)
        # significantly larger so item names are legible in placeholders
        self.item_font = pygame.font.SysFont(None, 28)

        # UI state
        self.selected_category = categories[0] if categories else None
        self.selected_item = None

        # caches / elements
        self.category_buttons = []
        self.item_placeholders = []
        self.icon_cache = {}

        # initial layout: only create category buttons; no item boxes yet
        self._layout_categories(screen.get_width())

    def _layout_categories(self, width):
        padding = 10
        n = max(1, len(self.categories))
        btn_w = max(80, (width - padding * (n + 1)) // n)
        btn_h = 36
        x = padding
        self.category_buttons = []
        for cat in self.categories:
            btn = Button(x, padding, btn_w, btn_h, cat, lambda c=cat: self._select_category(c), font=self.small_font)
            self.category_buttons.append(btn)
            x += btn_w + padding

    def _select_category(self, category):
        self.selected_category = category
        if self.on_category_change:
            self.on_category_change(category)

    def set_items(self, items):
        """Create placeholders exactly for the number of items passed and populate them."""
        self.item_placeholders = []
        width = self.rect.w
        count = max(0, len(items))
        if count == 0:
            return

        ph_total = count * self.placeholder_size + (count - 1) * self.placeholder_gap
        start_x = max(10, (width - ph_total) // 2)  # center placeholders
        ph_y = 10 + 36 + 8  # padding + category btn height + gap

        x = start_x
        for i in range(count):
            r = pygame.Rect(x, ph_y, self.placeholder_size, self.placeholder_size)
            self.item_placeholders.append((r, items[i]))
            x += self.placeholder_size + self.placeholder_gap

    def clear_items(self):
        self.item_placeholders = []

    def get_item_at_pos(self, pos):
        """Return (item_dict, rect) if an item placeholder with an item exists at pos, else (None, None)."""
        for rect, item in self.item_placeholders:
            if rect.collidepoint(pos):
                return (item, rect)
        return (None, None)

    def create_item_surface(self, item, size):
        """Create a surface for drag preview from item (icon or fitted name)."""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        surf.fill((0,0,0,0))
        if not item:
            return surf
        icon_path = item.get("icon_path")
        if icon_path and os.path.exists(icon_path):
            try:
                img = pygame.image.load(icon_path).convert_alpha()
                img = pygame.transform.smoothscale(img, (size-8, size-8))
                surf.blit(img, ((size - img.get_width())//2, (size - img.get_height())//2))
                return surf
            except Exception:
                pass
        # fallback: draw short name centered
        name = item.get("name","")
        txt = self._render_text_fit(name, size-8)
        surf.blit(txt, ((size - txt.get_width())//2, (size - txt.get_height())//2))
        return surf

    def _render_text_fit(self, text, max_w, font=None):
        """Return a Surface with text rendered small enough to fit within max_w.
           Tries decreasing font sizes (relative to provided font) then truncates with ellipsis."""
        if font is None:
            font = self.small_font
        # attempt with the font's size (or a larger starting size) and then reduce
        base_size = max(12, font.get_height(), 28)
        for s in range(base_size, 7, -1):
            f = pygame.font.SysFont(None, s)
            w, h = f.size(text)
            if w <= max_w:
                return f.render(text, True, (230,230,230))
        f = pygame.font.SysFont(None, 8)
        txt = text
        while txt and f.size(txt + '…')[0] > max_w:
            txt = txt[:-1]
        return f.render((txt + '…') if txt else '…', True, (230,230,230))

    def _render_two_line(self, line1, line2, max_w, max_h):
        """Attempt to render two lines stacked to fit into max_w x max_h.
           Returns a surface containing both lines vertically."""
        color = (230,230,230)
        # try sizes from a larger starting height downwards for better readability
        start_size = max(12, self.item_font.get_height(), 28)
        for s in range(start_size, 7, -1):
            f = pygame.font.SysFont(None, s)
            w1, h1 = f.size(line1)
            w2, h2 = f.size(line2)
            total_h = h1 + h2 + 2
            if w1 <= max_w and w2 <= max_w and total_h <= max_h:
                surf = pygame.Surface((max_w, total_h), pygame.SRCALPHA)
                surf.fill((0,0,0,0))
                r1 = f.render(line1, True, color)
                r2 = f.render(line2, True, color)
                surf.blit(r1, ((max_w - r1.get_width())//2, 0))
                surf.blit(r2, ((max_w - r2.get_width())//2, h1 + 2))
                return surf
        # fallback: render single-line truncated
        return self._render_text_fit(line1 + " " + line2, max_w, font=self.item_font)

    def handle_event(self, event):
        # category buttons handle clicks
        for btn in self.category_buttons:
            btn.handle_event(event)

        # clicking an item placeholder - keep this so item click callback still works
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, item in self.item_placeholders:
                if rect.collidepoint(event.pos):
                    self.selected_item = item
                    if item and self.on_item_click:
                        self.on_item_click(item)
                    else:
                        print("Empty item slot clicked (category={})".format(self.selected_category))
                    break

    def draw(self):
        # bar background
        pygame.draw.rect(self.screen, (40, 40, 40), self.rect)

        # draw category buttons row (top)
        for idx, btn in enumerate(self.category_buttons):
            pygame.draw.rect(self.screen, (60, 60, 60), btn.rect)
            pygame.draw.rect(self.screen, (90, 90, 90), btn.rect, 1)

            # alignment: first right, second center, last right
            text_surf = self.small_font.render(btn.text, True, (255,255,255))
            if idx == 0:
                text_x = btn.rect.right - 8 - text_surf.get_width()
            elif idx == 1:
                text_x = btn.rect.centerx - text_surf.get_width() // 2
            else:
                text_x = btn.rect.right - 8 - text_surf.get_width()
            text_y = btn.rect.centery - text_surf.get_height() // 2
            self.screen.blit(text_surf, (text_x, text_y))

            if btn.text == self.selected_category:
                pygame.draw.rect(self.screen, (200, 200, 60), pygame.Rect(btn.rect.x, btn.rect.bottom - 3, btn.rect.w, 3))

        # draw item placeholders row (below categories) - only if populated
        for rect, item in self.item_placeholders:
            pygame.draw.rect(self.screen, (60, 60, 60), rect)
            pygame.draw.rect(self.screen, (120, 120, 120), rect, 2)
            if item:
                icon_path = item.get("icon_path")
                if icon_path:
                    if icon_path not in self.icon_cache:
                        try:
                            if os.path.exists(icon_path):
                                surf = pygame.image.load(icon_path).convert_alpha()
                                surf = pygame.transform.smoothscale(surf, (rect.w-8, rect.h-8))
                                self.icon_cache[icon_path] = surf
                            else:
                                self.icon_cache[icon_path] = None
                        except Exception:
                            self.icon_cache[icon_path] = None
                    surf = self.icon_cache.get(icon_path)
                    if surf:
                        self.screen.blit(surf, (rect.x + (rect.w - surf.get_width())//2, rect.y + (rect.h - surf.get_height())//2))
                    else:
                        name = item.get("name","")
                        # if name has two words, render stacked; otherwise single-line
                        if len(name.split()) == 2:
                            w1, w2 = name.split()
                            txt = self._render_two_line(w1, w2, rect.w - 8, rect.h - 8)
                            self._blit_text_centered(txt, rect)
                        else:
                            txt = self._render_text_fit(name, rect.w-8, font=self.item_font)
                            self._blit_text_centered(txt, rect)
                else:
                    name = item.get("name","")
                    if len(name.split()) == 2:
                        w1, w2 = name.split()
                        txt = self._render_two_line(w1, w2, rect.w - 8, rect.h - 8)
                        self._blit_text_centered(txt, rect)
                    else:
                        txt = self._render_text_fit(name, rect.w-8, font=self.item_font)
                        self._blit_text_centered(txt, rect)

    def _blit_text_centered(self, surf, rect):
        x = rect.centerx - surf.get_width() // 2
        y = rect.centery - surf.get_height() // 2
        self.screen.blit(surf, (x, y))

    def get_selected_category(self):
        return self.selected_category

    def get_selected_item(self):
        return self.selected_item

    def resize(self, width):
        self.rect.w = width
        self._layout_categories(width)
        if self.item_placeholders:
            items = [itm for (_, itm) in self.item_placeholders]
            self.set_items(items)
