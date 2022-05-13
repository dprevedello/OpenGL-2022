from OpenGL.GL import *
from pywavefront import Wavefront

import numpy


class Mesh:

    def __init__(self, file):
        # Carico la mesh dal file
        mesh = Wavefront(file)

        # Estraggo i vertici e i colori dai dati letti
        data = numpy.array([])
        for m_item in mesh.mesh_list:
            for mat in m_item.materials:
                data = numpy.append(data, mat.vertices)

        self.length = len(data)//6
        data = data.reshape(self.length, 2, 3).astype(numpy.float32)

        self.vertici = data[:, 1].reshape(-1)
        self.colori = data[:, 0].reshape(-1)

        # Ci facciamo dare un'area sulla memoria della GPU
        # per fare ciò creiamo un Vertex Array Object (VAO)
        self.vertex_bufferId = glGenBuffers(1)
        # Informiamo la pipeline che vogliamo operare sulla sua memoria
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        # Copiamo i dati in memoria
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.vertici), self.vertici, GL_STATIC_DRAW)

        # Ripetiamo tutto per i dati sui colori
        self.color_bufferId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_bufferId)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.colori), self.colori, GL_STATIC_DRAW)

        # Sganciamo dalla pipeline i buffer
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Imposto il formato dei poligoni da disegnare
        self.type = GL_TRIANGLES

    def draw(self):
        # Agganciamo il buffer dei vertici
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glEnableClientState(GL_VERTEX_ARRAY)

        # Agganciamo il buffer dei colori
        glBindBuffer(GL_ARRAY_BUFFER, self.color_bufferId)
        glColorPointer(3, GL_FLOAT, 0, None)
        glEnableClientState(GL_COLOR_ARRAY)

        glDrawArrays(self.type, 0, self.length)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)
