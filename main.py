from pygameGUI import *

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time

animation_angle = 0


def triangolo():
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(1, -1, 0)
    glEnd()


def disegna(zoom, rotx, roty, animate, canvas2D):
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, -5 + zoom)
    glRotatef(-rotx, 1, 0, 0)
    glRotatef(-roty, 0, 1, 0)

    global animation_angle
    glRotatef(animation_angle, 0, 1, 0)
    if animate:
        animation_angle += 0.02

    glPushMatrix()
    triangolo()
    glPopMatrix()

    canvas2D.draw()

    pygame.display.flip()


def main():
    pygame.init()
    window_size = width, height = 500, 500
    window = pygame.display.set_mode(window_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("3D Lab - ISIS Ponti")
    pygame.display.set_icon(pygame.image.load('icon.png'))

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, width / height, 0.1, 50.0)

    fps_text = Gl2D_Text("0 FPS")
    top_bar = FoldableBar({'fps': fps_text}, foldButton=False)
    canvas2D = Gl2D_Canvas(window_size).addWidget(top_bar)

    zoom = 0
    old_x, old_y, rotx, roty = 0, 0, 0, 0
    dragging = False
    animate = False
    fps = 0
    t0 = time.time()
    running = True
    while running:
        for event in pygame.event.get():
            # Uscita dal programma
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                running = False
            if event.type == pygame.KEYUP and event.unicode == 'q':
                running = False

            # Zoom in
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
                zoom += 0.5
            # Zoom out
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
                zoom -= 0.5

            # Rotazioni del modello
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
                old_x, old_y = event.pos
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    rotx = rotx - (event.pos[1] - old_y)
                    roty = roty - (event.pos[0] - old_x)
                    old_x, old_y = event.pos

            # Animazione
            if event.type == pygame.KEYUP and event.unicode == 'a':
                animate = not animate

        fps += 1
        if time.time() - t0 >= 0.5:
            fps_text.setText(f"{fps*2} FPS")
            fps = 0
            t0 = time.time()
        disegna(zoom, rotx, roty, animate, canvas2D)
    pygame.quit()


if __name__ == "__main__":
    main()
