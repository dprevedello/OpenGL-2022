import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def triangolo():
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(1, -1, 0)
    glEnd()


def disegna(zoom):
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, zoom)

    glPushMatrix()
    glRotatef(10, 0, 0, 1)
    glScalef(0.7, 0.5, 1)
    glTranslatef(0, 0, -1.0)
    glTranslatef(0, 0.5, 0)
    triangolo()
    glPopMatrix()

    pygame.display.flip()


def main():
    pygame.init()
    window_size = width, height = 500, 500
    window = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Lab - ISIS Ponti")
    pygame.display.set_icon(pygame.image.load('icon.png'))

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, width / height, 0.1, 50.0)

    zoom = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYUP and event.unicode == 'q':
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
                zoom += 0.5
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
                zoom -= 0.5
        disegna(zoom)
    pygame.quit()


if __name__ == "__main__":
    main()
