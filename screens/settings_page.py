import pygame
from ui.button import Button

class SettingsPage:
    def __init__(self, screen, font, small_font, show_fps, fullscreen, on_back, on_toggle_fps, on_toggle_fullscreen):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.show_fps = show_fps
        self.fullscreen = fullscreen
        self.on_toggle_fps = on_toggle_fps
        self.on_toggle_fullscreen = on_toggle_fullscreen

        self.fps_button = Button(300, 200, 200, 50, f"Show FPS: {'ON' if show_fps else 'OFF'}", self.toggle_fps, font=self.font)
        self.fullscreen_button = Button(300, 270, 200, 50, f"Fullscreen: {'ON' if fullscreen else 'OFF'}", self.toggle_fullscreen, font=self.font)
        self.back_button = Button(300, 340, 200, 50, "Back", on_back, font=self.font)

        self.buttons = [self.fps_button, self.fullscreen_button, self.back_button]

    def toggle_fps(self):
        self.show_fps = not self.show_fps
        self.fps_button.text = f"Show FPS: {'ON' if self.show_fps else 'OFF'}"
        self.fps_button.txt_surface = self.font.render(self.fps_button.text, True, (255,255,255))
        self.on_toggle_fps(self.show_fps)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.fullscreen_button.text = f"Fullscreen: {'ON' if self.fullscreen else 'OFF'}"
        self.fullscreen_button.txt_surface = self.font.render(self.fullscreen_button.text, True, (255,255,255))
        self.on_toggle_fullscreen(self.fullscreen)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self):
        title = self.font.render("Settings", True, (255,255,255))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 120))
        for button in self.buttons:
            button.draw(self.screen)
