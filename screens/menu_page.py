import pygame
from ui.button import Button

class MenuPage:
    def __init__(self, screen, font, small_font, on_start, on_settings, on_logout, on_quit):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.buttons = [
            Button(300, 200, 200, 50, "Start Simulation", on_start, font=self.font),
            Button(300, 270, 200, 50, "Settings", on_settings, font=self.font),
            Button(300, 340, 200, 50, "Log out", on_logout, font=self.font),
            Button(300, 410, 200, 50, "Quit", on_quit, font=self.font)
        ]

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)

    def draw(self):
        title = self.font.render("Main Menu", True, (255,255,255))
        self.screen.blit(title, (self.screen.get_width()//2 - title.get_width()//2, 120))
        for button in self.buttons:
            button.draw(self.screen)