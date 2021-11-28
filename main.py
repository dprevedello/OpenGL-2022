import pygame
from pygame.locals import *


def disegna(window):
    window.fill([255, 255, 255])
    pygame.display.update()


def main():
    pygame.init()
    window_size = (500, 500)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("3D Lab - ISIS Ponti")
    pygame.display.set_icon(pygame.image.load('icon.png'))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYUP and event.unicode == 'q':
                running = False
        disegna(window)
    pygame.quit()


if __name__ == "__main__":
    main()
