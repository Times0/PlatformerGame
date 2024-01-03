from math import floor
from random import randint
from typing import Optional

import neat
import pygame

import constants
from constants import SFX_VOLUME


class Player(pygame.sprite.Sprite):

    def __init__(self, net, genome):
        super().__init__()
        self.points: list[list[tuple[int, int]]] = []
        self.font = pygame.font.SysFont('Arial', 20)
        self.best_distance: int = 0
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
        self.max_vision_distance = 400
        self.vision = [0, 0, 0, 0, 0, 0, 0, 0]
        self.ends = [None] * len(self.vision)
        self.line_spacing = 60

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
        self.horizontal_movement = 0
        keys = pygame.key.get_pressed()
        if constants.HUMAN_PLAYING:
            if keys[pygame.K_RIGHT] or keys[pygame.K_a]:
                self.horizontal_movement += self.speed
                self.facing_right = True

            if keys[pygame.K_LEFT] or keys[pygame.K_d]:
                self.horizontal_movement -= self.speed
                self.facing_right = False

            if keys[pygame.K_SPACE]:
                self.jump()
        else:
            inputs = self.get_ai_vision_inputs()
            output = self.net.activate(inputs)
            # Bias for the right direction since the end of the level is on the right
            if output[0] > 0.2:
                self.horizontal_movement += self.speed
                self.facing_right = True
            if output[1] > 0.8:
                self.horizontal_movement -= self.speed
                self.facing_right = False
            if output[2] > 0.5:
                self.jump()

    def get_ai_vision_inputs(self):
        """Return the distance to the closest object in each direction"""
        res = []
        for i in range(len(self.vision)):
            if self.vision[i] == 0:
                res.append(0)
            else:
                distance = self.ends[i][0] - self.rect.centerx
                score = 100 / distance if distance > 0 else 0
                res.append(score)
        return res

    def get_status(self):
        if self.on_ground:
            if self.horizontal_movement == 0:
                self.status = 'idle'
            else:
                self.status = 'run'
        else:
            self.status = 'jump'

    def jump(self):
        if self.on_ground:
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

    def vision_start_point(self):
        return self.rect.centerx, self.rect.centery - 25

    def update_vision(self, terrain: pygame.sprite.Group):
        self.vision = [0] * len(self.vision)
        self.ends: list[Optional[tuple[int, int]]] = [None] * len(self.vision)
        self.points: list[list[tuple[int, int]]] = [[] for _ in range(len(self.vision))]
        # collision between line and tile
        self.interesting_rect = self.rect.copy().inflate(self.max_vision_distance * 1.5,
                                                         self.line_spacing * len(self.vision)).move(200, 0)

        interesting_tiles = [tile for tile in terrain if self.interesting_rect.colliderect(tile.rect)]
        interesting_tiles.sort(key=lambda tile: tile.rect.x)

        n = len(self.vision)
        m = 20
        start = self.vision_start_point()
        for i in range(n):
            flag = False
            end = (start[0] + self.max_vision_distance,
                   start[1] - (n // 2 - i) * self.line_spacing)
            for j in range(1, m + 1):
                x = int(start[0] + j * (end[0] - start[0]) / m)
                y = int(start[1] + j * (end[1] - start[1]) / m)
                point = (x, y)
                self.points[i].append(point)

                for tile in interesting_tiles:
                    if tile.rect.collidepoint(point):
                        self.vision[i] = 1
                        self.ends[i] = point
                        flag = True
                        break
                if flag:
                    break

    def draw(self, win, draw_vision=False):
        win.blit(self.image, self.rect)

        # draw fitness on top
        pygame.draw.rect(win, (0, 0, 0), (self.rect.x, self.rect.y - 20, 100, 20))
        text = self.font.render(f"Fitness: {self.genome.fitness}", True, (255, 255, 255))
        win.blit(text, (self.rect.x, self.rect.y - 20))

        if draw_vision:
            self.draw_vision(win)

    def draw_vision(self, win):
        if hasattr(self, "interesting_rect"):
            pygame.draw.rect(win, (0, 0, 0), self.interesting_rect, 1)
        for i in range(n := len(self.vision)):
            if self.vision[i] == 1:
                color = (255, 0, 0)
            elif self.vision[i] == 2:
                color = (255, 255, 0)
            elif self.vision[i] == 3:
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)

            if self.ends[i]:
                end = self.ends[i]
            else:
                end = (self.vision_start_point()[0] + self.max_vision_distance,
                       self.vision_start_point()[1] - (n // 2 - i) * self.line_spacing)
            pygame.draw.aaline(win, color, self.vision_start_point(), end)
            for point in self.points[i]:
                pygame.draw.circle(win, color, (int(point[0]), int(point[1])), 2)
