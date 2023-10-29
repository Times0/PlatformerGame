import os
import pygame
from constants import *


class LevelUI:
    # Class that manages the user interface within levels

    def __init__(self):
        # Initialize UI elements

        # Health asset
        heart_path = 'assets/ui/heart.png'
        self.heart_image = pygame.image.load(os.path.join(heart_path))
        self.heart_image = pygame.transform.scale_by(self.heart_image, (TILE_SIZE // self.heart_image.get_width()))

        # Coin asset
        coin_path = 'assets/ui/coin_icon.png'
        self.coin_image = pygame.image.load(os.path.join(coin_path))
        self.coin_image = pygame.transform.scale_by(self.coin_image, (TILE_SIZE // self.coin_image.get_width()))

        # Font and coin counter size
        font_path = 'assets/ui/Retro Gaming.ttf'
        self.font = pygame.font.Font(os.path.join(font_path), 30)

        self.enemy_path = "assets/ui/enemy.png"
        self.enemy_image = pygame.image.load(self.enemy_path)
        self.enemy_image = pygame.transform.scale_by(self.enemy_image, (TILE_SIZE // self.enemy_image.get_width()))

        self.bee_path = "assets/ui/bee.png"
        self.bee_image = pygame.image.load(self.bee_path)
        self.bee_image = pygame.transform.scale_by(self.bee_image, (TILE_SIZE // self.bee_image.get_width()))

    def draw_health(self, win, current_health):
        # Display the health counter

        for x in range(current_health):
            win.blit(self.heart_image, (10 + x * (self.heart_image.get_width() + 5), 10))

    def draw_coins_counter(self, win, nb_coin):
        # Display the level's coin counter

        win.blit(self.coin_image, (5, 10 + TILE_SIZE))

        text = '× ' + str(nb_coin)
        text_surface = self.font.render(text, False, (255, 196, 56))
        win.blit(text_surface, (TILE_SIZE, TILE_SIZE + 15))

    def draw_enemy_count(self, win, nb_goomba, nb_bee):
        self.draw_goomba_count(win, nb_goomba)
        self.draw_bee_count(win, nb_bee)

    def draw_goomba_count(self, win, nb_enemy):
        win.blit(self.enemy_image, (5, 10 + 2 * TILE_SIZE))

        text = '× ' + str(nb_enemy)
        text_surface = self.font.render(text, False, (23, 25, 27))
        win.blit(text_surface, (TILE_SIZE + 10, 2 * TILE_SIZE + 20))

    def draw_bee_count(self, win, nb_enemy):
        win.blit(self.bee_image, (5, 10 + 3 * TILE_SIZE))

        text = '× ' + str(nb_enemy)
        text_surface = self.font.render(text, False, (23, 25, 27))
        win.blit(text_surface, (TILE_SIZE + 10, 3 * TILE_SIZE + 20))

    def draw(self, win, nb_coins, nb_goomba, nb_bee, health):
        # Draw the UI elements including enemy counts, health, and coin counter

        self.draw_enemy_count(win, nb_goomba, nb_bee)
        self.draw_health(win, health)
        self.draw_coins_counter(win, nb_coins)


class Button:
    # Class for creating buttons in the game

    def __init__(self, x, y, text, width=150, height=150, click=None):

        self.x = x
        self.y = y

        font_path = 'assets/ui/Retro Gaming.ttf'

        self.click = click

        self.text = text
        self.font = pygame.font.Font(os.path.join(font_path), 50)

        self.color = (105, 222, 222)
        self.outline_color = (0, 0, 0)

        self.width = width
        self.height = height

        self.rect = pygame.Rect((x, y), (self.width, self.height))
        self.outline_rect = pygame.Rect(x - 2, y - 2, self.rect.width + 4, self.rect.height + 4)

        self.text_image = self.font.render(self.text, False, (0, 0, 0))
        self.text_rect = self.text_image.get_rect(center=self.rect.center)

    def draw(self, screen):
        # Draw the button with text

        # Button outline
        pygame.draw.rect(screen, self.outline_color, self.outline_rect, 0)

        # Button background
        pygame.draw.rect(screen, self.color, self.rect)

        # Button text
        screen.blit(self.text_image, self.text_rect)

    def on_mouse_clicked(self, event):
        # Function that returns True if the click is on the button

        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.rect.collidepoint(event.pos)

    def on_mouse_motion(self, event):
        # Function to change the button color when the mouse hovers over it

        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.color = (255, 255, 255)
            else:
                self.color = (105, 222, 222)

    def select(self):
        # Change the button color when selected

        self.color = (255, 255, 255)

    def unselect(self):
        # Restore the default button color when deselected

        self.color = (105, 222, 222)
