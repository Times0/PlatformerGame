import os

import pygame
from pytmx.util_pygame import load_pygame

from constants import *
from enemy import Goomba, Bee
from player import Player
from tile import Tile, AnimatedTile
from ui import LevelUI


class Level:
    def __init__(self, current_level, show_menu, show_gameover):
        self.current_level: int = current_level
        self.show_menu = show_menu
        self.show_gameover = show_gameover

        # User interface within the level
        self.ui = LevelUI()
        self.nb_coins = 0

        # Player setup
        self.player: Player = Player()
        self.scroll = False
        self.nb_goomba = 0
        self.nb_bee = 0
        self.nb_isib = 0

        # Level setup
        self.sprite_groups = []
        self.setup_level()
        self.center_camera()

        # Sound effects (SFX)
        coin_volume = 2 * SFX_VOLUME
        self.coin_sfx = pygame.mixer.Sound('assets/sounds/coin_2.mp3')
        self.coin_sfx.set_volume(coin_volume)

    def setup_level(self):
        # Function that imports the game map

        # Import the TMX file
        path = 'assets/levels/level' + str(self.current_level) + '.tmx'  # Retrieve the current level's file
        level_data = load_pygame(os.path.join(path))

        # Terrain:
        layer = level_data.get_layer_by_name('Terrain')
        self.terrain = self.create_sprite_group(layer)
        self.sprite_groups.append(self.terrain)

        # Decoration:
        layer = level_data.get_layer_by_name('Decoration')
        self.decoration = self.create_sprite_group(layer)
        self.sprite_groups.append(self.decoration)

        # Background:
        layer = level_data.get_layer_by_name('Background')
        self.background = self.create_sprite_group(layer)
        self.sprite_groups.append(self.background)

        # Player
        layer = level_data.get_layer_by_name('Spawn')
        for x, y, surface in layer.tiles():
            player_spawn_x = x * TILE_SIZE
            player_spawn_y = (y + 1) * TILE_SIZE
            self.player.rect.bottomleft = (player_spawn_x, player_spawn_y)

        # Enemies
        layer = level_data.get_layer_by_name('Enemies')
        self.enemies = pygame.sprite.Group()

        for x, y, surface in layer.tiles():
            tile = Goomba(x, y, surface)  # Create a new "Tile" object with its position and image
            self.enemies.add(tile)  # Add this tile to the group

        # Bee enemies
        layer = level_data.get_layer_by_name('Bees')
        for x, y, surface in layer.tiles():
            tile = Bee(x, y, surface)  # Create a new "Tile" object with its position and image
            self.enemies.add(tile)  # Add this tile to the group

        self.sprite_groups.append(self.enemies)

        # Enemy boundaries:
        layer = level_data.get_layer_by_name('EnemyBoundaries')
        self.enemy_boundaries = self.create_sprite_group(layer)
        self.sprite_groups.append(self.enemy_boundaries)

        # Coins:
        layer = level_data.get_layer_by_name('Coins')
        path = 'assets/animations/coin.png'
        self.coins = self.create_sprite_group(layer, 'animated', path)
        self.sprite_groups.append(self.coins)

        # Deep water:
        layer = level_data.get_layer_by_name('DeepWater')
        path = 'assets/animations/deep_water.png'
        self.deep_water = self.create_sprite_group(layer, 'animated', path)
        self.sprite_groups.append(self.deep_water)

        # Surface water:
        layer = level_data.get_layer_by_name('SurfaceWater')
        path = 'assets/animations/surface_water.png'
        self.surface_water = self.create_sprite_group(layer, 'animated', path)
        self.sprite_groups.append(self.surface_water)

        # Foreground:
        layer = level_data.get_layer_by_name('Foreground')
        self.foreground = self.create_sprite_group(layer)
        self.sprite_groups.append(self.foreground)

        # Doors:
        layer = level_data.get_layer_by_name('Doors')
        self.doors = self.create_sprite_group(layer)
        self.sprite_groups.append(self.doors)

        # Finish:
        layer = level_data.get_layer_by_name('Finish')
        self.finish = self.create_sprite_group(layer)
        self.sprite_groups.append(self.finish)

    @staticmethod
    def create_sprite_group(layer, tile_type='static', path=''):

        sprite_group = pygame.sprite.Group()

        for x, y, surface in layer.tiles():
            if tile_type == 'static':
                tile = Tile(x, y, surface)  # Create a new "Tile" object with its position and image
                sprite_group.add(tile)  # Add this tile to the group

            elif tile_type == 'animated':
                tile = AnimatedTile(x, y, surface, path)  # Create a new animated tile
                sprite_group.add(tile)  # Add this tile to the group

        return sprite_group

    def horizontal_collision(self, dt):

        # Apply the player's horizontal movement:
        if not self.scroll:  # If the camera has moved all the sprites, no need to move the player
            x_offset = self.player.horizontal_movement * dt
            self.player.rect.x += x_offset

        collision = pygame.sprite.spritecollide(self.player, self.terrain, False)

        for tile in collision:

            # Collisions on the right of the player
            if self.player.horizontal_movement > 0:
                self.player.rect.right = tile.rect.left

            # Collisions on the left of the player
            elif self.player.horizontal_movement < 0:
                self.player.rect.left = tile.rect.right

    def vertical_collision(self, dt):
        # Apply the player's vertical movement:

        y_offset = self.player.vertical_movement * dt
        self.player.rect.y += y_offset

        collision = pygame.sprite.spritecollide(self.player, self.terrain, False)

        for tile in collision:

            # Collisions below the player
            if self.player.vertical_movement > 0:
                self.player.rect.bottom = tile.rect.top
                self.player.vertical_movement = 0
                self.player.on_ground = True

            # Collisions above the player
            elif self.player.vertical_movement < 0:
                self.player.rect.top = tile.rect.bottom
                self.player.vertical_movement = 0

        # if self.player.vertical_movement > 0:
        #     self.player.on_ground = False

    def check_coin_collision(self):
        # Function to collect coins when the player touches them

        collision = pygame.sprite.spritecollide(self.player, self.coins, False)

        if collision:
            for coin in collision:
                self.nb_coins += 1
                self.coin_sfx.play()
                coin.kill()

                # MODIFIED HERE
                if self.nb_coins == COIN_REQUIRED:
                    self.draw(self.win)  # Draw the whole level again to show the x/x coins and not x-1/x coins
                    self.show_gameover(self.current_level, win=True, nb_coin=self.nb_coins)

    def check_enemy_collision(self):
        # Function to check enemy collisions with their boundaries and the player

        for enemy in self.enemies.sprites():

            # Collision with enemy boundaries to determine when they turn
            collision = pygame.sprite.spritecollide(enemy, self.enemy_boundaries, False)

            if collision:
                for tile in collision:

                    # Collisions on the right of the enemy
                    if enemy.horizontal_movement > 0:
                        enemy.rect.right = tile.rect.left
                        enemy.horizontal_movement = -enemy.speed

                    # Collisions on the left of the enemy
                    elif enemy.horizontal_movement < 0:
                        enemy.rect.left = tile.rect.right
                        enemy.horizontal_movement = enemy.speed

            # Collision between the enemy and the player
            collision = enemy.rect.colliderect(self.player.rect)

            if collision and enemy.status != 'hurt':  # Collision with a live enemy

                # If the player jumps on the enemy
                if self.player.rect.bottom < enemy.rect.centery and self.player.vertical_movement > 0:
                    self.player.vertical_movement = - self.player.jump_power / 2
                    enemy.die()
                    if enemy.__class__.__name__ == 'Goomba':
                        self.nb_goomba += 1
                    elif enemy.__class__.__name__ == 'Bee':
                        self.nb_bee += 1
                    elif enemy.__class__.__name__ == 'Isib':
                        self.nb_isib += 1
                    else:
                        pass

                elif self.player.rect.bottom < enemy.rect.centery and self.player.vertical_movement < 0:
                    pass

                # If the player is hit by the enemy and is not invincible
                elif not self.player.invincible:
                    self.player.take_damage()
                    if self.player.current_lives <= 0:
                        self.show_gameover(self.current_level)

    def check_finish(self):

        finish_collision = pygame.sprite.spritecollide(self.player, self.finish, False)

        if finish_collision:
            self.show_gameover(self.current_level, win=True, nb_coin=self.nb_coins)

    def check_player_death(self):
        if self.player.rect.top > HEIGHT:
            self.show_gameover(self.current_level)

    def reset_player(self):
        # Reset the level and the player

        self.nb_coins = 0
        self.player.current_lives = self.player.lives

        self.player.vertical_movement = 0
        self.player.horizontal_movement = 0
        self.player.rect.x = 0
        self.player.rect.y = 0

        self.player.on_ground = False
        self.player.facing_right = True
        self.player.invincible = False
        self.player.first_run = True

        self.sprite_groups = []
        self.setup_level()
        self.center_camera()

    def center_camera(self):
        # Place the player in the center of the screen

        # Calculate the offset between the center of the screen and the player
        offset = round(WIDTH / 2 - self.player.rect.centerx)

        # Move the player
        self.player.rect.centerx += offset

        # Move all other sprites
        for sprite_group in self.sprite_groups:
            for sprite in sprite_group:
                sprite.rect.x += offset

    def camera_scroll(self, dt):
        # Function that scrolls the camera horizontally

        # Indicator to avoid moving the player if we are moving all other objects
        self.scroll = False
        if self.player.rect.right > WIDTH / 2:  # If the player is on the right side of the screen
            if self.player.horizontal_movement > 0:  # If the player is moving to the right
                # Move all sprites to the left
                offset = self.player.horizontal_movement * dt
                for sprite_group in self.sprite_groups:
                    for sprite in sprite_group:
                        sprite.rect.x -= offset
                        self.scroll = True

        elif self.player.rect.left < WIDTH / 4:  # If the player is on the left side of the screen
            if self.player.horizontal_movement < 0:  # If the player is moving to the left
                # Move all sprites to the left
                offset = self.player.horizontal_movement * dt
                for sprite_group in self.sprite_groups:
                    for sprite in sprite_group:
                        sprite.rect.x -= offset
                        self.scroll = True

    def update(self, dt):
        # Main function that runs the game within the levels
        # Update the player:
        self.player.update(dt)
        self.check_coin_collision()
        self.check_finish()

        # Update the enemies:
        self.enemies.update(dt)
        self.check_enemy_collision()

        # Camera scroll:
        self.camera_scroll(dt)

        # Player collisions
        self.horizontal_collision(dt)
        self.vertical_collision(dt)

        # water
        self.surface_water.update()
        self.deep_water.update()

        self.check_player_death()

    def draw(self, win):
        self.win = win
        win.fill((51, 165, 255))  # Fill the window with a blue background

        self.background.draw(win)
        self.decoration.draw(win)
        self.terrain.draw(win)
        self.coins.draw(win)
        self.player.draw(win)
        self.enemies.draw(win)
        self.deep_water.draw(win)
        self.foreground.draw(win)
        self.doors.draw(win)

        self.ui.draw(win, nb_coins=self.nb_coins,
                     nb_goomba=self.nb_goomba,
                     nb_bee=self.nb_bee,
                     health=self.player.current_lives)

        pygame.display.flip()
