import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def disegna():
    # R=0 G=0 B=0 A=1
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glPushMatrix()

    glRotatef(10, 0, 0, 1)
    glScalef(0.7, 0.5, 1)
    glTranslatef(0, 0, -1.0)
    glTranslatef(0, 0.5, 0)

    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(1, -1, 0)
    glEnd()

    glPopMatrix()

    pygame.display.flip()


def main():
    pygame.init()
    window_size = (500, 500)
    window = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
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
        disegna()
    pygame.quit()


if __name__ == "__main__":
    main()
