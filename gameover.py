# Import necessary libraries
import pygame
from ui import Button  # Import the Button class from the 'ui' module
from constants import *  # Import constant values like WINDOW_WIDTH and HEIGHT
import os


# Define the 'Gameover' class
class Gameover:
    def __init__(self, create_level, show_menu):
        # Initialize variables and callbacks
        self.current_level = 1
        self.create_level = create_level  # Callback function for creating a level
        self.show_menu = show_menu  # Callback function for showing the main menu
        self.input_cooldown = 300  # Cooldown time for user input
        self.last_input = self.input_cooldown  # Time of the last user input

        # Title setup
        font_path = 'assets/ui/Retro Gaming.ttf'  # Path to the font file
        self.font = pygame.font.Font(os.path.join(font_path), 50)  # Create a font with a specific size
        self.title_image = None  # Title text image
        self.title_rect = None  # Rectangle to position the title text

        # Buttons setup
        self.buttons = []  # List to store buttons
        self.button_selected = 0  # Index of the currently selected button

    def handle_events(self, events):
        # Handle user events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse clicks on buttons
                for button in self.buttons:
                    if button.on_mouse_clicked(event):
                        button.click(self.current_level)

            elif event.type == pygame.MOUSEMOTION:
                # Change button colors when the mouse hovers over them
                for button in self.buttons:
                    button.on_mouse_motion(event)

            elif event.type == pygame.KEYDOWN:
                # Handle keyboard input
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    # Change the selected button downwards
                    self.buttons[self.button_selected].unselect()
                    self.button_selected += 1
                    if self.button_selected > len(self.buttons) - 1:
                        self.button_selected = 0
                    self.buttons[self.button_selected].select()

                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                    # Change the selected button upwards
                    self.buttons[self.button_selected].unselect()
                    self.button_selected -= 1
                    if self.button_selected < 0:
                        self.button_selected = len(self.buttons) - 1
                    self.buttons[self.button_selected].select()

                elif event.key == pygame.K_SPACE:
                    # Click on the selected button when the space key is pressed
                    self.buttons[self.button_selected].click(self.current_level)

            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    # Handle controller input (pressing the first button)
                    self.buttons[self.button_selected].click(self.current_level)

    def draw(self, win):
        # Draw the game over screen
        win.blit(self.title_image, self.title_rect)  # Draw the title text
        for button in self.buttons:
            button.draw(win)  # Draw all buttons
        pygame.display.flip()  # Update the display


# Define the 'DefeatScreen' class, which is a subclass of 'Gameover'
class DefeatScreen(Gameover):
    def __init__(self, create_level, show_menu):
        super().__init__(create_level, show_menu)  # Call the constructor of the 'Gameover' class

        # Customize defeat screen title
        self.title = 'Game Over'  # Set the title text
        red = (255, 0, 0)  # Red color for the title
        self.title_image = self.font.render(self.title, False, red)  # Render the title text
        self.title_rect = self.title_image.get_rect(centerx=WIDTH / 2, y=50)  # Position the title text

        # Create restart button
        button_width = 450
        button_height = 100
        button_x = (WIDTH - button_width) / 2
        button_y = HEIGHT / 2 - button_height
        self.restart_btn = Button(button_x, button_y, text='Restart', width=button_width, height=button_height,
                                  click=self.create_level)

        # Create return to menu button
        button_x = (WIDTH - button_width) / 2
        button_y = HEIGHT / 2 + button_height / 2
        self.menu_btn = Button(button_x, button_y, text='Back to menu', width=button_width, height=button_height,
                               click=self.show_menu)

        # Store buttons and select the first one
        self.buttons = [self.restart_btn, self.menu_btn]
        self.button_selected = 0
        self.restart_btn.select()


# Define the 'VictoryScreen' class, which is also a subclass of 'Gameover'
class VictoryScreen(Gameover):
    def __init__(self, create_level, show_menu, next_level):
        super().__init__(create_level, show_menu)  # Call the constructor of the 'Gameover' class

        # Store the callback function for the next level
        self.next_level = next_level

        # Customize victory screen title
        self.title = 'You win!'  # Set the title text
        green = (0, 255, 0)  # Green color for the title
        self.title_image = self.font.render(self.title, False, green)  # Render the title text
        self.title_rect = self.title_image.get_rect(centerx=WIDTH / 2, y=50)  # Position the title text

        # Create next level button
        button_width = 450
        button_height = 100
        button_x = (WIDTH - button_width) / 2
        button_y = HEIGHT / 2 - 2 * button_height
        self.next_level_btn = Button(button_x, button_y, text='Next level', width=button_width, height=button_height,
                                     click=self.next_level)

        # Create restart button
        button_x = (WIDTH - button_width) / 2
        button_y = (HEIGHT - button_height) / 2
        self.restart_btn = Button(button_x, button_y, text='Restart', width=button_width, height=button_height,
                                  click=self.create_level)

        # Create return to menu button
        button_x = (WIDTH - button_width) / 2
        button_y = HEIGHT / 2 + button_height
        self.menu_btn = Button(button_x, button_y, text='Back to menu', width=button_width, height=button_height,
                               click=self.show_menu)

        # Store buttons and select the first one
        self.buttons = [self.next_level_btn, self.restart_btn, self.menu_btn]
        self.button_selected = 0
        self.restart_btn.select()
