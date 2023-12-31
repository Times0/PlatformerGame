# Import necessary modules and constants
from math import floor, sin
from typing import Optional

import pygame
from constants import *
from tile import Tile


# Define the base class for all enemies
class Enemy(Tile):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        # Initialize enemy properties
        self.speed: Optional[int] = None
        self.horizontal_movement = 0
        self.facing_right = True
        self.status = 'idle'
        self.animation_sprites = {'idle': [], 'run': [], 'hurt': []}
        self.frame_index = 0
        self.animation_speed = 10

        # Sound effects
        self.explosion_sfx = pygame.mixer.Sound('assets/sounds/Explosion.wav')
        self.explosion_sfx.set_volume(SFX_VOLUME)

    def animate(self, dt):
        # Function to manage the enemy's displayed image based on its state and animation progress

        # Get the current animation state
        current_animation = self.animation_sprites[self.status]

        # Update the animation frame index
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.status == 'hurt':
                self.kill()

        # Retrieve the image for the animation
        image = current_animation[floor(self.frame_index)]

        # Flip the image if the enemy is facing left
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False).convert_alpha()

        self.image = image

    def get_status(self):
        # Function to change the enemy's state for animations (idle, running, hurt)
        if self.status != 'hurt':
            if self.horizontal_movement == 0:
                self.status = 'idle'
            elif self.horizontal_movement > 0:
                self.status = 'run'
                self.facing_right = True
            elif self.horizontal_movement < 0:
                self.status = 'run'
                self.facing_right = False

    def move(self, dt):
        self.rect.x += self.horizontal_movement * dt

    def die(self):
        # Function to handle the enemy's death
        self.horizontal_movement = 0
        self.status = 'hurt'
        self.explosion_sfx.play()
        self.frame_index = 2

    def update(self, dt):
        # Update the enemy's status, movement, and animation
        self.get_status()
        self.move(dt)
        self.animate(dt)


# Define a subclass of Enemy for Goomba enemies
class Goomba(Enemy):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)

        # Customize Goomba-specific properties and load its animation sprites
        self.status = 'idle'
        self.speed = 200
        self.horizontal_movement = self.speed
        self.animation_sprites = {'idle': [], 'run': [], 'hurt': []}
        self.frame_index = 0
        self.load_sprites()
        self.image = self.animation_sprites[self.status][0]

    def load_sprites(self):
        # Load Goomba's animation sprites from a sprite sheet

        sprite_sheet_path = 'assets/animations/enemy.png'
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        sprite_sheet = pygame.transform.scale_by(sprite_sheet, self.resize_factor)

        for key in self.animation_sprites:
            if key == 'idle':
                y = 0
                nb_sprite = 8
            elif key == 'run':
                y = 16
                nb_sprite = 6
            else:
                y = 32
                nb_sprite = 4
            # Define coordinates on the sprite sheet for each animation type

            for i in range(nb_sprite):
                surface = pygame.Surface((self.width, self.width)).convert_alpha()
                surface.set_colorkey((0, 0, 0))
                surface.blit(sprite_sheet, (0, 0), (
                    i * 16 * self.resize_factor, y * self.resize_factor, 16 * self.resize_factor,
                    28 * self.resize_factor))

                self.animation_sprites[key].append(surface)


# Define a subclass of Enemy for Bee enemies
class Bee(Enemy):
    def __init__(self, x, y, image):
        super().__init__(x, y, image)
        self.speed = 250
        self.horizontal_movement = self.speed
        self._y = y * TILE_SIZE
        self.status = 'run'
        self.animation_sprites = {'run': [], 'hurt': []}
        self.frame_index = 0
        self.load_sprites()
        self.image = self.animation_sprites[self.status][0]

    def load_sprites(self):
        # Load Bee's animation sprites from a sprite sheet

        sprite_sheet_path = 'assets/animations/bee.png'
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        sprite_sheet = pygame.transform.scale_by(sprite_sheet, self.resize_factor)

        for key in self.animation_sprites:
            # Define coordinates on the sprite sheet for each animation type
            if key == 'run':
                y = 0
                nb_sprite = 4
            else:
                y = 16
                nb_sprite = 3

            for i in range(nb_sprite):
                surface = pygame.Surface((self.width, self.width)).convert_alpha()
                surface.set_colorkey((0, 0, 0))
                surface.blit(sprite_sheet, (0, 0), (
                    i * 16 * self.resize_factor, y * self.resize_factor, 16 * self.resize_factor,
                    28 * self.resize_factor))

                self.animation_sprites[key].append(surface)
