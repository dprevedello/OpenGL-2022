import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from win32con import *
from win32gui import *
from OpenGL.GL import *
from pygame.locals import *
import pygame


def windowSize(window=None):
    if window is None:
        window = GetForegroundWindow()
    rect = GetWindowRect(window)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    return w, h


def wndProc(oldWndProc, draw_callback, hWnd, message, wParam, lParam):
    if message == WM_SIZE:
        draw_callback()
        RedrawWindow(hWnd, None, None, RDW_INVALIDATE | RDW_ERASE)
    return CallWindowProc(oldWndProc, hWnd, message, wParam, lParam)


class Gl2D_Text:
    def __init__(self, text: str, x: int = 0, y: int = 0, color="White", font="Arial", size=18, 
                 bold=False, italic=False, border=False, borderColor="White", radius=0, bg=False, 
                 bgColor="Gray", overBgColor=None, clickColor=None):
        self.x, self.y = x, y
        self.color = color
        self.font = pygame.font.SysFont(font, size, bold=bold, italic=italic)
        self.padding = max(size // 3, 2)
        self.border = border
        self.borderColor = borderColor
        self.radius = radius
        self.bg = bg
        self.bgColor = bgColor
        self.overBgColor = overBgColor
        self.clickColor = clickColor
        self.setText(text)
        self._setGuiManager(None)

    def _setGuiManager(self, manager):
        self._GuiManager = manager

    def setText(self, text):
        textSurface = self.font.render(text, True, self.color).convert_alpha()
        tw, th = textSurface.get_size()

        if self.border:
            borderSurface = pygame.Surface((tw + self.padding * 2, th + self.padding * 2), SRCALPHA)
            rect = pygame.Rect((0, 0), borderSurface.get_size())
            pygame.draw.rect(borderSurface, self.borderColor, rect, 2, self.radius)
            borderSurface.blit(textSurface, (self.padding, self.padding))
            surface = borderSurface
        else:
            surface = textSurface

        if self.bg:
            bgSurface = pygame.Surface((tw + self.padding * 2, th + self.padding * 2), SRCALPHA)
            rect = pygame.Rect((0, 0), bgSurface.get_size())
            pygame.draw.rect(bgSurface, self.bgColor, rect, 0, self.radius)
            if self.border:
                bgSurface.blit(surface, (0, 0))
            else:
                bgSurface.blit(surface, (self.padding, self.padding))

            if self.overBgColor:
                bgAltSurface = pygame.Surface((tw + self.padding * 2, th + self.padding * 2), SRCALPHA)
                rect = pygame.Rect((0, 0), bgAltSurface.get_size())
                pygame.draw.rect(bgAltSurface, self.overBgColor, rect, 0,
                                 self.radius)
                if self.border:
                    bgAltSurface.blit(surface, (0, 0))
                else:
                    bgAltSurface.blit(surface, (self.padding, self.padding))
                self.textAltData = pygame.image.tostring(bgAltSurface, "RGBA", True)

            if self.clickColor:
                bgClickSurface = pygame.Surface((tw + self.padding * 2, th + self.padding * 2), SRCALPHA)
                rect = pygame.Rect((0, 0), bgClickSurface.get_size())
                pygame.draw.rect(bgClickSurface, self.clickColor, rect, 0,
                                 self.radius)
                if self.border:
                    bgClickSurface.blit(surface, (0, 0))
                else:
                    bgClickSurface.blit(surface, (self.padding, self.padding))
                self.textClickData = pygame.image.tostring(bgClickSurface, "RGBA", True)

            surface = bgSurface

        self.width, self.height = surface.get_size()
        self.textData = pygame.image.tostring(surface, "RGBA", True)

    def draw(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glWindowPos2d(self.x, self.y)
        if self.bg and self.overBgColor and self.isMouseOver():
            if self.clickColor and pygame.mouse.get_pressed()[0]:
                glDrawPixels(self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, self.textClickData)
            else:
                glDrawPixels(self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, self.textAltData)
        else:
            glDrawPixels(self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE, self.textData)
        glDisable(GL_BLEND)

    def isMouseOver(self):
        mx, my = pygame.mouse.get_pos()
        
        if self._GuiManager is None:
            w, h = pygame.display.get_surface().get_size()
        else:
            w, h = self._GuiManager.window_size
            
        return mx >= self.x and h - my >= self.y and mx <= self.x + \
            self.width and h - my <= self.y + self.height


class FoldableBar():
    def __init__(self, content=None, position="top", foldButton=True, folded=False, padding=5):
        self.content = {
            "fold": Gl2D_Text("<", border=True)
        } if foldButton else {}
        if isinstance(content, dict):
            self.content.update(content)
        self.position = position
        self.foldButton = foldButton
        self.folded = folded
        self.padding = padding
        self.window_decorations = (0, 0)
        self.maxHeight = max(map(lambda x: x.height, self.content.values()))
        self.window = GetForegroundWindow()
        self._setGuiManager(None)

    def _setGuiManager(self, manager):
        self._GuiManager = manager
        if manager is not None:
            self.window_decorations = [
                s1 - s2 for s1, s2 in zip(windowSize(self.window), manager.window_size)
            ]
        for widget in self.content.values():
            widget._setGuiManager(manager)

    def addItem(self, item, name):
        if item and name:
            self.content[name] = item
            item._setGuiManager(self._GuiManager)
        return self

    def draw(self):
        if self.position == "top":
            self._drawTop()
        else:
            self._drawBottom()

    def _drawTop(self):
        w, h = [
            s1 - s2 for s1, s2 in zip(windowSize(self.window), self.window_decorations)
        ]
        y = h - self.padding - self.maxHeight
        x = self.padding
        for widget in self.content.values():
            widget.x, widget.y = x, y + (self.maxHeight - widget.height) // 2
            widget.draw()
            x += widget.width + self.padding
            if self.folded:
                return

    def _drawBottom(self):
        y = self.padding
        x = self.padding
        for widget in self.content.values():
            widget.x, widget.y = x, y + (self.maxHeight - widget.height) // 2
            widget.draw()
            x += widget.width + self.padding
            if self.folded:
                return

    def overElement(self):
        for name, element in self.content.items():
            if element.isMouseOver():
                return name
        return None


class Gl2D_Canvas():
    def __init__(self, window_size):
        self.widgets = []
        self.window_size = window_size

    def setSize(self, window_size):
        self.window_size = window_size

    def addWidget(self, *widgets):
        for widget in widgets:
            self.widgets.append(widget)
            widget._setGuiManager(self)
        return self

    def draw(self):
        for widget in self.widgets:
            widget.draw()

    def overElement(self):
        for widget in self.widgets:
            if (name := widget.overElement()) is not None:
                return name
        return None
