from math import floor
from random import randint

import pygame

from constants import *


class Player(pygame.sprite.Sprite):

    def __init__(self):
        super().__init__()

        # Caractéristiques principales du joueur
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

        # Utilitaires
        self.vertical_movement = 0
        self.horizontal_movement = 0
        self.on_ground = True
        self.facing_right = True

        # Chargement des sprites du joueur
        self.status = 'idle'
        self.animation_sprites = {'idle': [], 'jump': [], 'run': []}
        self.resize_factor = self.width / 14
        self.frame_index = 0
        self.animation_speed = 10
        self.load_sprites()
        self.image = self.animation_sprites[self.status][self.frame_index]

        # SFX
        self.jump_sfx = pygame.mixer.Sound('assets/sounds/Jump.wav')
        self.jump_sfx.set_volume(SFX_VOLUME)

        hurt_volume = 2 * SFX_VOLUME
        self.hurt_sfx = pygame.mixer.Sound('assets/sounds/Hurt.wav')
        self.hurt_sfx.set_volume(hurt_volume)

    def load_sprites(self):
        # Fonction qui récupère les images d'animation du joueur dans la sprite sheet

        sprite_sheet_path = 'assets/animations/Hero.png'
        sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        sprite_sheet = pygame.transform.scale_by(sprite_sheet, (
            self.resize_factor))

        for key in self.animation_sprites:
            # On récupère les coordonnées sur la sprite sheet de chaque type d'animation
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
        # Fonction qui gère l'image du joueur à afficher selon l'état du joueur et la progression de l'animation

        # état du joueur :
        current_animation = self.animation_sprites[self.status]

        # boucle d'animation (index de progression de l'animation)
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0

        # récupération de l'image de l'animation
        image = current_animation[floor(self.frame_index)]

        # Inversion de l'image selon la direction dans laquelle regarde le joueur
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False).convert_alpha()

        # Clignotement lorsque le joueur est invincible
        if self.invincible:
            alpha = randint(0, 255)
            image.set_alpha(alpha)
        else:
            image.set_alpha(255)

        self.image = image

    def get_inputs(self):
        # Fonction qui gère les actions du joueur

        # Réinitialisation de la vitesse horizontale
        self.horizontal_movement = 0

        # d'abord les actions du clavier
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT] or keys[pygame.K_a]:
            self.horizontal_movement += self.speed
            self.facing_right = True

        if keys[pygame.K_LEFT] or keys[pygame.K_d]:
            self.horizontal_movement -= self.speed
            self.facing_right = False

        if keys[pygame.K_SPACE]:
            if self.on_ground:  # s'il est sur le sol
                self.jump()

    def get_status(self):
        # Fonction qui change l'état du joueur pour les animations (immobile, en train de courir, de sauter...)

        if self.on_ground:
            if self.horizontal_movement == 0:
                self.status = 'idle'
            else:
                self.status = 'run'
        else:
            self.status = 'jump'

    def jump(self):
        # Fonction qui fait sauter le joueur

        self.vertical_movement -= self.jump_power
        self.on_ground = False
        self.jump_sfx.play()

    def apply_gravity(self, dt):
        # Fonction qui ajoute la gravité à la vitesse verticale du joueur
        if not self.first_run:
            self.vertical_movement += self.gravity * dt
        else:
            self.vertical_movement += self.gravity * 0.016
            self.first_run = False

    def check_invincibility(self):
        # vérifie le timer d'invincibilité

        if self.invincible:
            now = pygame.time.get_ticks()
            if now - self.invincibility_timer > self.invincibility_period:
                self.invincible = False

    def take_damage(self):

        # Rend le joueur invincible pendant un certain temps
        self.invincible = True
        self.invincibility_timer = pygame.time.get_ticks()

        self.hurt_sfx.play()

        # une vie en moins
        self.current_lives -= 1

    def update(self, dt):
        # Actualisation du joueur
        self.get_inputs()
        self.apply_gravity(dt)
        self.check_invincibility()
        self.get_status()
        self.animate(dt)

        # Les collisions se font dans la classe Level pour avoir accès aux blocs du terrain

    def draw(self, win):
        # Dessin du joueur
        win.blit(self.image, self.rect)
