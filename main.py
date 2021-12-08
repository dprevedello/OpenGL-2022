from pygameGUI import *

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

import sys


class Scena:

    def __init__(self, width, height, frame_rate):
        # Frame rate
        self.frame_rate = frame_rate
        # Zoom
        self.zoom = 0
        # Trackball
        self.old_x, self.old_y = 0, 0
        self.rotx, self.roty = 0, 0
        self.dragging = False
        # Animazione
        self.animate = False
        self.animation_angle = 0
        # Contatore FPS
        self.fps = [frame_rate / 2] * 4
        self.fps_timer = pygame.USEREVENT
        pygame.time.set_timer(self.fps_timer, 500)
        # Clock per regolare il Frame Rate
        self.clock = pygame.time.Clock()
        # Fullscreen
        self.fullscreen = False
        # Interfaccia 2D visibile
        self.interface_2D = True
        # Scena visibile
        self.destroyed = False

        self.window_id = GetForegroundWindow()
        self.decorations = [
            s1 - s2
            for s1, s2 in zip(windowSize(self.window_id), (width, height))
        ]

        self._build_2D_interface(width, height)
        self.setup(width, height)
        self.oldWndProc = SetWindowLong(
            self.window_id, GWL_WNDPROC, lambda *args: wndProc(
                self.oldWndProc, self._update_on_resize, *args))

    def _build_2D_interface(self, width, height):
        self.animate_button = Gl2D_Text("ANIM",
                                        border=True,
                                        radius=5,
                                        bg=True,
                                        bgColor="#B2473D",
                                        overBgColor="#D22C1D",
                                        clickColor="#A4160A")
        self.fullscreen_button = Gl2D_Text("FULL",
                                           border=True,
                                           radius=5,
                                           bg=True,
                                           bgColor="#8AB23D",
                                           overBgColor="#A4D21D",
                                           clickColor="#6AA40A")
        self.bottom_bar = FoldableBar(
            {
                'animate': self.animate_button,
                'fullscreen': self.fullscreen_button
            },
            position="bottom")
        self.bottom_bar.content['fold'].setText('◄')

        self.fps_text = Gl2D_Text("")
        self.top_bar = FoldableBar({'fps': self.fps_text}, foldButton=False)

        self.canvas2D = Gl2D_Canvas((width, height))
        self.canvas2D.addWidget(self.top_bar, self.bottom_bar)
        self.update_FPS()

    def setup(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 50.0)

    def _update_on_resize(self, *args):
        if not self.destroyed:
            width, height = [
                s1 - s2
                for s1, s2 in zip(windowSize(self.window_id), self.decorations)
            ] if not self.fullscreen else windowSize(self.window_id)
            self.setup(width, height)
            self.canvas2D.setSize((width, height))
            self.draw()

    def _pre_draw(self):
        # Aggiornamento FPS
        self.fps[0] += 1

        # Cancello il canvas
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        # Imposto la telecamera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(0, 0, -5 + self.zoom)
        glRotatef(-self.rotx, 1, 0, 0)
        glRotatef(-self.roty, 0, 1, 0)

    def draw(self):
        self._pre_draw()

        glRotatef(self.animation_angle, 0, 1, 0)
        if self.animate:
            self.animation_angle += (360 / 5 / self.frame_rate)

        glPushMatrix()
        triangolo()
        glPopMatrix()

        if self.interface_2D:
            self.canvas2D.draw()
        self._post_draw()

    def _post_draw(self):
        pygame.display.flip()
        # Impostiamo il frame rate
        self.clock.tick(self.frame_rate)

    def destroy(self):
        self.destroyed = True

    def zoom_in(self):
        self.zoom += 0.5

    def zoom_out(self):
        self.zoom -= 0.5

    def trackball(self, dragging, position=None):
        self.dragging = dragging
        if position:
            self.old_x, self.old_y = position

    def update_trackball(self, position):
        if self.dragging:
            self.rotx -= (position[1] - self.old_y)
            self.roty -= (position[0] - self.old_x)
            self.old_x, self.old_y = position

    def toggle_animation(self):
        self.animate = not self.animate

    def update_FPS(self):
        self.fps_text.setText(f"{sum(self.fps)/4*2:.1f} FPS")
        self.fps = [0, self.fps[0], self.fps[1], self.fps[2]]

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        pygame.display.toggle_fullscreen()

    def on_click_2D(self):
        if self.interface_2D:
            element = self.canvas2D.overElement()
            if not self.bottom_bar.folded:
                if element == 'animate':
                    self.toggle_animation()
                elif element == 'fullscreen':
                    self.toggle_fullscreen()
            if element == 'fold':
                self.bottom_bar.folded = not self.bottom_bar.folded
                if self.bottom_bar.folded:
                    self.bottom_bar.content['fold'].setText('►')
                else:
                    self.bottom_bar.content['fold'].setText('◄')

    def toggle_interface_2D(self):
        self.interface_2D = not self.interface_2D


def triangolo():
    glBegin(GL_TRIANGLES)
    glColor3f(1, 0, 0)
    glVertex3f(-1, -1, 0)
    glColor3f(0, 1, 0)
    glVertex3f(0, 1, 0)
    glColor3f(0, 0, 1)
    glVertex3f(1, -1, 0)
    glEnd()


def main():
    pygame.init()
    window_size = width, height = 500, 500
    window = pygame.display.set_mode(window_size,
                                     DOUBLEBUF | OPENGL | RESIZABLE)
    pygame.display.set_caption("3D Lab - ISIS Ponti")
    pygame.display.set_icon(pygame.image.load('icon.png'))

    scena = Scena(width, height, 60)

    running = True
    while running:
        for event in pygame.event.get():
            # Uscita dal programma
            if event.type == pygame.QUIT or \
               event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE or \
               event.type == pygame.KEYUP and event.unicode == 'q':
                scena.destroy()
                running = False

            # Zoom in
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_PLUS:
                scena.zoom_in()
            # Zoom out
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 5 or \
               event.type == pygame.KEYDOWN and event.key == pygame.K_MINUS:
                scena.zoom_out()

            # Trackball
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scena.trackball(True, event.pos)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                scena.trackball(False)
            if event.type == pygame.MOUSEMOTION:
                scena.update_trackball(event.pos)

            # Animazione
            if event.type == pygame.KEYUP and event.unicode == 'a':
                scena.toggle_animation()

            # Contatore FPS
            if event.type == scena.fps_timer:
                scena.update_FPS()

            # Attivazione full screen
            if event.type == pygame.KEYUP and event.unicode == 'f':
                scena.toggle_fullscreen()

            # Resize
            if event.type == pygame.VIDEORESIZE:
                window_size = width, height = event.size
                scena.setup(width, height)

            # Interazione con l'interfaccia 2D
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                scena.on_click_2D()

            # Disattivazione / attivazione interfaccia 2D
            if event.type == pygame.KEYUP and event.unicode == 'i':
                scena.toggle_interface_2D()
        scena.draw()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
