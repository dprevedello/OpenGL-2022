import pygame
from pygame.locals import *


def disegna(window):
    window.fill([255, 255, 255])
    pygame.display.update()


def main():
    pygame.init()
    window_size = (500, 500)
    window = pygame.display.set_mode(window_size)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        disegna(window)
    pygame.quit()


if __name__ == "__main__":
    main()
