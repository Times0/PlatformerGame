import pygame.sprite
from constants import *  # Importing constants (not shown in the provided code).
from math import floor


# Define a class called "Tile" that inherits from pygame.sprite.Sprite.
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()

        self.width = TILE_SIZE  # Set the width of the tile to a constant value (TILE_SIZE).

        # Load the image and resize it to fit the tile size.
        self.resize_factor = TILE_SIZE / image.get_width()
        self.image = pygame.transform.scale_by(image, self.resize_factor)

        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE  # Set the x-coordinate of the tile.
        self.rect.y = y * TILE_SIZE  # Set the y-coordinate of the tile.


# Define a class called "AnimatedTile" that inherits from the "Tile" class.
class AnimatedTile(Tile):
    def __init__(self, x, y, image, path):
        super().__init__(x, y, image)

        self.path = path  # Store the path to a sprite sheet image.
        self.tile_width = 16  # Set the width of a single tile in the sprite sheet.
        self.resize_factor = TILE_SIZE / self.tile_width  # Calculate the resize factor.

        self.frame_index = 0  # Initialize the frame index for animation.
        self.animation_speed = 0.1  # Set the animation speed.
        self.animation_sprites = list()  # Create an empty list to store animation frames.
        self.load_sprites()  # Load animation frames from the sprite sheet.

    # Load animation frames from the sprite sheet.
    def load_sprites(self):
        sprite_sheet = pygame.image.load(self.path).convert_alpha()
        nb_sprites = int(sprite_sheet.get_width() / self.tile_width)
        sprite_sheet = pygame.transform.scale_by(sprite_sheet, (self.resize_factor))

        for x in range(nb_sprites):
            surface = pygame.Surface((self.width, self.width), pygame.SRCALPHA).convert_alpha()
            surface.set_colorkey((0, 0, 0))
            surface.blit(sprite_sheet, (0, 0), (x * TILE_SIZE, 0, TILE_SIZE, TILE_SIZE))

            self.animation_sprites.append(surface)

    # Function to animate the tile by changing its image based on the animation progress.
    def animate(self):
        # Animation loop (progress index of the animation).
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animation_sprites):
            self.frame_index = 0

        # Get the current animation frame.
        self.image = self.animation_sprites[floor(self.frame_index)]

    # Update method to be called in the game loop, which updates the animation.
    def update(self):
        self.animate()
