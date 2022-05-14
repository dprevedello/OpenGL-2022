from OpenGL.GL import *
from pywavefront import Wavefront

import numpy
import glm


class Mesh:

    def __init__(self, file):
        # Carico la mesh dal file
        mesh = Wavefront(file)

        # Estraggo i vertici e i colori dai dati letti
        data = numpy.array([])
        for m_item in mesh.mesh_list:
            for mat in m_item.materials:
                data = numpy.append(data, mat.vertices)

        # N. di triangoli da disegnare
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

        # Compilo gli shaders
        self.shaders_ok = self._compila_shaders()

    def _compila_shaders(self):
        vertex_shader = """
            #version 330 core

            // Dati in input, variabili per ciascun vertice
            // ATTENZIONE agli indici scelti
            layout(location = 0) in vec3 vertexPosition_modelspace;
            layout(location = 1) in vec3 vertexColor;

            // Dati in output, interpolati per ciascun frammento
            out vec3 fragmentColor;

            // Valori passati allo shader che rimangono costanti
            uniform mat4 MVP;

            void main(){
                // Calcolo della posizione del vertice in clip space: MVP * position
                gl_Position =  MVP * vec4(vertexPosition_modelspace, 1);

                // Il colore di ciascun vertice viene interpolato per
                // ottenere il colore di ciascun frammento
                fragmentColor = vertexColor;
            }
        """

        fragment_shader = """
            #version 330 core

            // Valori interpolati forniti dal vertex shader
            in vec3 fragmentColor;

            // Dati in output
            out vec3 color;

            void main(){
                color = fragmentColor;
            }
        """

        # Creo un nuovo identificatore per il programma della GPU
        self.program = glCreateProgram()

        # vertex shader
        vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vs, vertex_shader)
        glCompileShader(vs)
        if GL_TRUE != glGetShaderiv(vs, GL_COMPILE_STATUS):
            print(glGetShaderInfoLog(vs))
            return False
        glAttachShader(self.program, vs)

        # fragment shader
        fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fs, fragment_shader)
        glCompileShader(fs)
        if GL_TRUE != glGetShaderiv(vs, GL_COMPILE_STATUS):
            print(glGetShaderInfoLog(vs))
            return False
        glAttachShader(self.program, fs)

        glLinkProgram(self.program)
        if GL_TRUE != glGetProgramiv(self.program, GL_LINK_STATUS):
            print(glGetProgramInfoLog(self.program))
            return False

        self.MVP_uniform = glGetUniformLocation(self.program, "MVP")
        return True

    def draw(self, model, view, projection):
        if not self.shaders_ok:
            return

        # Calcolo la matrice model-view-projection
        # NOTA: fare attenzione all'ordine in cui compaiono!
        MVP = projection * view * model

        # Impostiamo il programma che la GPU deve usare
        glUseProgram(self.program)

        # Associo la matrice MVP corrente al proprio uniform
        glUniformMatrix4fv(self.MVP_uniform, 1, GL_FALSE, glm.value_ptr(MVP))

        # Agganciamo il buffer dei vertici all'indice 0
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Agganciamo il buffer dei colori all'indice 1
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.color_bufferId)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)

        glDrawArrays(self.type, 0, self.length * 3)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

        # Disabilito il programma sulla GPU
        glUseProgram(0)

        # Sganciamo dalla pipeline i buffer
        glBindBuffer(GL_ARRAY_BUFFER, 0)
