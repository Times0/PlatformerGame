# Import necessary modules and classes
import enum

import pygame.sprite
from pygame.locals import *
from constants import *
from data_loader import get_player_data, update_player_data
from gameover import VictoryScreen, DefeatScreen
from level import Level
from menu import Menu

# Define the path to the data file
DATA_PATH = 'data/data.json'


class GameState(enum.Enum):
    MENU = 0
    LEVEL = 1
    WIN = 2
    LOSE = 3


# Define the Game class
class Game:
    def __init__(self, win):
        self.ai_playing = False
        self.win = win
        self.game_is_on = True  # This variable will be used to stop the game

        # Load player data and set the maximum level
        data = get_player_data(DATA_PATH)
        self.max_level = len(data)

        # Initialize game music
        self.level_music = pygame.mixer.Sound('assets/sounds/level_music.wav')
        self.level_music.set_volume(MUSIC_VOLUME)
        self.menu_music = pygame.mixer.Sound('assets/sounds/menu_music.wav')
        self.menu_music.set_volume(MUSIC_VOLUME)
        win_volume = 4 * MUSIC_VOLUME
        self.win_music = pygame.mixer.Sound('assets/sounds/victory_music.mp3')
        self.win_music.set_volume(win_volume)
        death_volume = 4 * MUSIC_VOLUME
        self.death_music = pygame.mixer.Sound('assets/sounds/death_music.mp3')
        self.death_music.set_volume(death_volume)

        # Menu setup
        self.menu = Menu(self.max_level, 1, self.create_level, data)
        self.menu_music.play(loops=-1)
        self.level = None
        self.game_state = GameState.MENU

        # Gameover screens
        self.win_screen = VictoryScreen(self.create_level, self.show_menu, self.next_level)
        self.lose_screen = DefeatScreen(self.create_level, self.show_menu)

    def init_bot(self, genomes=None, config=None):
        self.ai_playing = True
        self.genomes = genomes
        self.config = config

    def create_level(self, current_level):
        # Stop any playing music, play level music, and create a new level
        self.death_music.stop()
        self.win_music.stop()
        self.menu_music.stop()
        self.level_music.play(loops=-1)
        self.level = Level(current_level, self.show_menu, self.show_game_over, self.genomes, self.config)
        self.game_state = GameState.LEVEL

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS) / 1000  # Calculate time passed since the last frame
            # print(f"FPS: {clock.get_fps()}")
            dt = min(dt, 0.1)  # Cap the maximum time passed to 0.1 seconds to avoid crash with slow pc
            self.handle_events()  # Handle game events
            self.update(dt)  # Update the game state
            self.draw(self.win)  # Draw the game on the window

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                self.game_is_on = False

        if self.game_state == GameState.MENU:
            self.menu.handle_events(events)
        elif self.game_state == GameState.WIN:
            self.win_screen.handle_events(events)
        elif self.game_state == GameState.LOSE:
            self.lose_screen.handle_events(events)

    def update(self, dt):
        if self.game_state == GameState.LEVEL:
            self.level.update(dt)

    def draw(self, win):
        # Draw the game on the window based on the game state
        if self.game_state == GameState.LEVEL:
            self.level.draw(win)
        elif self.game_state == GameState.MENU:
            self.menu.draw(win)
        elif self.game_state == GameState.WIN:
            self.win_screen.draw(win)
        elif self.game_state == GameState.LOSE:
            self.lose_screen.draw(win)

    def show_menu(self, current_level):
        # Stop music, set the menu to the current level, and play menu music
        self.death_music.stop()
        self.win_music.stop()
        self.menu.max_level = self.max_level
        self.menu.current_level = current_level
        for button in self.menu.buttons:
            button.unselect()
        self.menu.buttons[current_level - 1].select()
        self.level_music.stop()
        self.menu_music.play(loops=-1)
        self.game_state = GameState.MENU

    def show_game_over(self, current_level, win=False, nb_coin=0):
        # Create a black filter screen, stop music, and set the game state based on win or lose
        black_filter = pygame.Surface((WIDTH, HEIGHT))
        black_filter.fill((0, 0, 0))
        black_filter.set_alpha(200)
        self.win.blit(black_filter, (0, 0))
        pygame.display.flip()
        self.menu_music.stop()
        self.level_music.stop()

        if win:
            self.game_state = GameState.WIN
            self.win_music.play()
            if update_player_data(DATA_PATH, current_level, nb_coin):
                self.menu.update_nb_coins(current_level, nb_coin)
            for button in self.win_screen.buttons:
                button.unselect()
            self.win_screen.buttons[0].select()
            self.win_screen.button_selected = 0
            self.win_screen.current_level = current_level
        else:
            self.game_state = GameState.LOSE
            self.death_music.play()
            for button in self.lose_screen.buttons:
                button.unselect()
            self.lose_screen.buttons[0].select()
            self.lose_screen.button_selected = 0
            self.lose_screen.current_level = current_level

    def next_level(self, current_level):
        if current_level < self.max_level:
            # Update the menu and create the next level
            self.menu.current_level = current_level + 1
            self.win_screen.current_level = current_level + 1
            self.lose_screen.current_level = current_level + 1
            self.create_level(current_level + 1)
