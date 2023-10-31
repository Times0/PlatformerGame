from math import floor
from random import randint

import pygame

from constants import *


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        # Player's main characteristics
        self.lives = 3
        self.current_lives = self.lives
        self.width = 49
        self.height = 2 * self.width
        self.speed = 550
        self.gravity = 3000
        self.jump_power = 1150
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_period = 1000
        self.first_run = True

        self.rect = pygame.rect.Rect(0, 0, self.width, self.height)

        # Utilities
        self.vertical_movement = 0
        self.horizontal_movement = 0
        self.on_ground = True
        self.facing_right = True

        # Loading player's animation sprites
        self.status = 'idle'
        self.animation_sprites = {'idle': [], 'jump': [], 'run': []}
        self.resize_factor = self.width / 14
        self.frame_index = 0
        self.animation_speed = 10
        self.load_sprites()
        self.image = self.animation_sprites[self.status][self.frame_index]

        # Sound Effects (SFX)
        self.jump_sfx = pygame.mixer.Sound('assets/sounds/Jump.wav')
        self.jump_sfx.set_volume(SFX_VOLUME)

        hurt_volume = 2 * SFX_VOLUME
        self.hurt_sfx = pygame.mixer.Sound('assets/sounds/Hurt.wav')
        self.hurt_sfx.set_volume(hurt_volume)

    def load_sprites(self):
        # Function to retrieve player's animation images from the sprite sheet

        sprite_sheet_path = 'assets/animations/Hero.png'
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        sprite_sheet = pygame.transform.scale_by(sprite_sheet, (
            self.resize_factor))

        for key in self.animation_sprites:
            # Retrieve the coordinates on the sprite sheet for each type of animation
            if key == 'idle':
                y = 20
                nb_sprite = 8
            elif key == 'jump':
                y = 52
                nb_sprite = 4
            elif key == 'run':
                y = 84
                nb_sprite = 4

            for i in range(nb_sprite):
                surface = pygame.Surface((self.width, self.height)).convert_alpha()
                surface.set_colorkey((0, 0, 0))
                surface.blit(sprite_sheet, (0, 0),
                             (i * 16 * self.resize_factor, y * self.resize_factor, 16 * self.resize_factor,
                              28 * self.resize_factor))

                self.animation_sprites[key].append(surface)

    def animate(self, dt):
        # Function to handle the player's image to display based on the player's state and animation progress

        # Player's state:
        current_animation = self.animation_sprites[self.status]

        # Animation loop (index for animation progression)
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        # Get the image for the animation
        image = current_animation[floor(self.frame_index)]

        # Flip the image based on the player's direction
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False).convert_alpha()

        # Blink when the player is invincible
        if self.invincible:
            alpha = randint(0, 255)
            image.set_alpha(alpha)
        else:
            image.set_alpha(255)

        self.image = image

    def get_inputs(self):
        # Function to handle player's actions

        # Reset horizontal speed
        self.horizontal_movement = 0

        # Keyboard actions
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_a]:
            self.horizontal_movement += self.speed
            self.facing_right = True

        if keys[pygame.K_LEFT] or keys[pygame.K_d]:
            self.horizontal_movement -= self.speed
            self.facing_right = False

        if keys[pygame.K_SPACE]:
            if self.on_ground:
                self.jump()

    def get_status(self):
        # Function to change the player's state for animations (idle, running, jumping...)

        if self.on_ground:
            if self.horizontal_movement == 0:
                self.status = 'idle'
            else:
                self.status = 'run'
        else:
            self.status = 'jump'

    def jump(self):
        # Function to make the player jump

        self.vertical_movement -= self.jump_power
        self.on_ground = False
        self.jump_sfx.play()

    def apply_gravity(self, dt):
        # Function to add gravity to the player's vertical speed
        if not self.first_run:
            self.vertical_movement += self.gravity * dt
        else:
            self.vertical_movement += self.gravity * 0.016
            self.first_run = False

    def check_invincibility(self):
        # Check the invincibility timer

        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincibility_timer > self.invincibility_period:
                self.invincible = False

    def take_damage(self):
        # Make the player invincible for a certain period of time
        self.invincible = True
        self.invincibility_timer = pygame.time.get_ticks()
        self.hurt_sfx.play()
        self.current_lives -= 1

    def update(self, dt):
        # Update the player
        self.get_inputs()
        self.apply_gravity(dt)
        self.check_invincibility()
        self.get_status()
        self.animate(dt)

        # Collisions are handled in the Level class to have access to the terrain blocks

    def draw(self, win):
        # Draw the player
        win.blit(self.image, self.rect)
