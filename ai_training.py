# neat
import neat
import pygame
from constants import WIDTH, HEIGHT

from game import Game


def main(genomes, config):
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(win)
    game.init_bot(genomes=genomes, config=config)
    game.run()


def run():
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, 'config.txt')

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    winner = population.run(main)


if __name__ == '__main__':
    run()
