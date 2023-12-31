import time

import pygame
from ui import Button
import os
from constants import *


class Menu:
    def __init__(self, max_level, current_level, create_level, data):
        # Initialize the Menu class with various attributes and resources.

        # Get the display surface of the game window.
        self.display_surface = pygame.display.get_surface()

        # Define timing variables for input control.
        self.input_cooldown = 300
        self.last_input = 301

        # Store information about game levels.
        self.max_level = max_level  # The maximum available level.
        self.current_level = current_level  # The currently selected level.
        self.create_level = create_level  # A function to start a game level.

        # Load and configure the background image.
        background_path = 'assets/ui/background.png'
        self.background = pygame.image.load(os.path.join(background_path))
        self.background = pygame.transform.scale_by(self.background, 1200 / 1056)
        self.background = self.background.convert()

        # Load and configure assets for coins.
        font_path = 'assets/ui/Retro Gaming.ttf'
        self.coin_font = pygame.font.Font(os.path.join(font_path), 25)
        coin_path = 'assets/ui/coin_icon.png'
        self.coin_image = pygame.image.load(os.path.join(coin_path))
        self.coin_image = pygame.transform.scale(self.coin_image, (TILE_SIZE, TILE_SIZE))
        self.coin_image = self.coin_image.convert_alpha()

        # Create the title for the menu.
        self.font = pygame.font.Font(os.path.join(font_path), 50)
        title = 'Select a level:'
        self.title_image = self.font.render(title, False, (0, 0, 0))
        self.title_rect = self.title_image.get_rect(centerx=WIDTH / 2, y=50)

        # Store level data.
        self.data = data

        # Create buttons for selecting levels.
        self.buttons = []
        self.coins_info = []  # Information about the number of coins for each level.
        for index, level_data in enumerate(data.values()):
            button = Button(100 + index * 200, 200, text=str(index + 1))
            self.buttons.append(button)

            # Create a UI element to display the coin count.
            coin_surface = self.create_coin_ui(level_data[0], level_data[1])
            self.coins_info.append(coin_surface)

        # Initially select the current level's button.
        self.buttons[self.current_level - 1].select()

    def update_nb_coins(self, level, new_value):
        # Update the displayed coin count for a specific level.

        key = 'level' + str(level)
        total_coin = self.data[key][1]
        new_coin_surface = self.create_coin_ui(new_value, total_coin)
        self.coins_info[level - 1] = new_coin_surface

    def create_coin_ui(self, nb_coin, total_coin):
        # Create a visual element for displaying the coin count of a level.

        text = str(nb_coin) + '/' + str(total_coin)
        black = (0, 0, 0)
        text_surface = self.coin_font.render(text, False, black)

        width = text_surface.get_width() + self.coin_image.get_width()
        height = self.coin_image.get_height()

        surface = pygame.Surface((width, height)).convert()
        surface.fill((255, 255, 255))
        surface.set_colorkey((255, 255, 255))
        surface.set_alpha(200)

        surface.blit(self.coin_image, (0, 0))

        text_pos_y = (height - text_surface.get_height()) / 2
        surface.blit(text_surface, (self.coin_image.get_width() - 5, text_pos_y))

        return surface

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Start the selected level if a button is clicked.
                for button in self.buttons:
                    if button.on_mouse_clicked(event):
                        self.create_level(int(button.text))
                        # ignore other events
                        return

            elif event.type == pygame.MOUSEMOTION:
                # Change the button's color when the mouse hovers over it.
                for button in self.buttons:
                    button.on_mouse_motion(event)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_a:
                    # Change the selected level using the right arrow key or 'A' key.

                    self.buttons[self.current_level - 1].unselect()
                    self.current_level += 1
                    if self.current_level > self.max_level:
                        self.current_level = 1
                    self.buttons[self.current_level - 1].select()

                elif event.key == pygame.K_LEFT or event.key == pygame.K_d:
                    # Change the selected level using the left arrow key or 'D' key.

                    self.buttons[self.current_level - 1].unselect()
                    self.current_level -= 1
                    if self.current_level < 1:
                        self.current_level = self.max_level
                    self.buttons[self.current_level - 1].select()

                elif event.key == pygame.K_SPACE:
                    # Start the currently selected level when the space key is pressed.
                    self.create_level(self.current_level)
                    return

    def draw(self, win):
        # Draw the menu on the game window.
        win.blit(self.background, (0, 0))
        win.blit(self.title_image, self.title_rect)
        for index, button in enumerate(self.buttons):
            button.draw(win)
            coin_surface = self.coins_info[index]
            pos = (button.x, button.y)
            win.blit(coin_surface, pos)
        pygame.display.flip()
