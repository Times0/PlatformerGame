from math import floor
from random import randint

import neat
import pygame

import constants
from constants import *


class Player(pygame.sprite.Sprite):

    def __init__(self, net, genome):
        super().__init__()
        self.font = pygame.font.SysFont('Arial', 20)
        self.best_distance: int = 0
        self.terrains = None
        self.net = net
        self.genome: neat.DefaultGenome = genome
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

        # AI vision
        self.max_vision_distance = 200
        self.vision = [0, 0, 0, 0, 0, 0]  # 0 = empty, 1 = block, 2 = coin, 3 = enemy
        self.line_spacing = 40

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
            else:
                raise Exception('Invalid animation key')
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
            image = pygame.transform.flip(image, True, False)

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
        if constants.HUMAN_PLAYING:
            if keys[pygame.K_RIGHT] or keys[pygame.K_a]:
                self.horizontal_movement += self.speed
                self.facing_right = True

            if keys[pygame.K_LEFT] or keys[pygame.K_d]:
                self.horizontal_movement -= self.speed
                self.facing_right = False

            if keys[pygame.K_SPACE]:
                if self.on_ground:
                    self.jump()
        else:
            inputs = self.get_ai_vision_inputs() + [self.on_ground] + [self.facing_right]
            inputs = [e * 100 for e in inputs]
            output = self.net.activate(inputs)
            if output[0] > 0.5:
                self.horizontal_movement += self.speed
                self.facing_right = True
            if output[1] > 0.5:
                self.horizontal_movement -= self.speed
                self.facing_right = False
            if output[2] > 0.5:
                if self.on_ground:
                    self.jump()

    def get_ai_vision_inputs(self):
        return self.vision

    def get_status(self):
        if self.on_ground:
            if self.horizontal_movement == 0:
                self.status = 'idle'
            else:
                self.status = 'run'
        else:
            self.status = 'jump'

    def jump(self):
        self.vertical_movement -= self.jump_power
        self.on_ground = False
        self.jump_sfx.play()

    def apply_gravity(self, dt):
        if not self.first_run:
            self.vertical_movement += self.gravity * dt
        else:
            self.vertical_movement += self.gravity * 0.016
            self.first_run = False

    def check_invincibility(self):
        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincibility_timer > self.invincibility_period:
                self.invincible = False

    def take_damage(self):
        self.invincible = True
        self.invincibility_timer = pygame.time.get_ticks()
        self.hurt_sfx.play()
        self.current_lives -= 1

    def update(self, dt):
        self.get_inputs()
        self.apply_gravity(dt)
        self.check_invincibility()
        self.get_status()
        self.animate(dt)
        # Collisions are handled in the Level class to have access to the terrain blocks

    def draw(self, win, draw_vision=True):
        win.blit(self.image, self.rect)

        # draw fitness on top
        pygame.draw.rect(win, (0, 0, 0), (self.rect.x, self.rect.y - 20, 100, 20))
        text = self.font.render(f"Fitness: {self.genome.fitness}", True, (255, 255, 255))
        win.blit(text, (self.rect.x, self.rect.y - 20))

        if draw_vision:
            self.draw_vision(win)

    def draw_vision(self, win):
        for i in range(n := len(self.vision)):
            if self.vision[i] == 1:
                color = (255, 0, 0)
            elif self.vision[i] == 2:
                color = (255, 255, 0)
            elif self.vision[i] == 3:
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)
            pygame.draw.aaline(win, color,
                               self.vision_start_point(),
                               (self.vision_start_point()[0] + self.max_vision_distance,
                                self.vision_start_point()[1] - (n // 2 - i) * self.line_spacing))

    def vision_start_point(self):
        return self.rect.centerx, self.rect.centery - 25

    def update_vision(self, terrain: pygame.sprite.Group):
        self.vision = [0, 0, 0, 0, 0, 0]
        if not self.terrains:
            self.terrains = sorted(terrain.sprites(), key=lambda t: t.rect.x)
        # collision between line and tile
        for tile in self.terrains:
            if tile.rect.x > self.rect.x + self.max_vision_distance:
                break
            if tile.rect.x + tile.rect.width < self.rect.x - self.max_vision_distance:
                continue
            if tile.rect.y + tile.rect.height < self.rect.y - self.max_vision_distance:
                continue
            if tile.rect.y > self.rect.y + self.max_vision_distance:
                continue

            # collision between line and tile
            start_point = self.vision_start_point()
            for i in range(n := len(self.vision)):
                end_point = (start_point[0] + self.max_vision_distance,
                             start_point[1] - (n // 2 - i) * self.line_spacing)
                # extract m points from line using linear interpolation
                m = 10
                for j in range(m + 1):
                    x = start_point[0] + (end_point[0] - start_point[0]) * j / m
                    y = start_point[1] + (end_point[1] - start_point[1]) * j / m
                    if tile.rect.collidepoint(x, y):
                        self.vision[i] = 1
                        break
