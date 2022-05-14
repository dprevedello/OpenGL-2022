from OpenGL.GL import *
from pywavefront import Wavefront

import numpy
import glm
import cv2


class Mesh:

    def __init__(self, file, texture_path):
        # Carico la mesh dal file
        mesh = Wavefront(file)
        print(mesh.mesh_list[0].materials[0].vertex_format)

        # Estraggo i vertici e i le coordinate UV dai dati letti
        data = numpy.array([])
        for m_item in mesh.mesh_list:
            for mat in m_item.materials:
                data = numpy.append(data, mat.vertices)

        # N. di triangoli da disegnare
        self.length = len(data)//8
        data = data.reshape(self.length, 8).astype(numpy.float32)

        self.vertici = data[:, 5:8].reshape(-1)
        self.texel = data[:, 0:2].reshape(-1)

        # Ci facciamo dare un'area sulla memoria della GPU
        # per fare ciò creiamo un Vertex Array Object (VAO)
        self.vertex_bufferId = glGenBuffers(1)
        # Informiamo la pipeline che vogliamo operare sulla sua memoria
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        # Copiamo i dati in memoria
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.vertici), self.vertici, GL_STATIC_DRAW)

        # Ripetiamo tutto per i dati sulle coordinate UV
        self.texel_bufferId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.texel_bufferId)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.texel), self.texel, GL_STATIC_DRAW)

        # Sganciamo dalla pipeline i buffer
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Carichiamo sulla memoria della GPU la texture della mesh
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        img = cv2.flip(cv2.imread(texture_path), 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.shape[1], img.shape[0], 0, GL_BGR, GL_UNSIGNED_BYTE, img.data)
        glGenerateMipmap(GL_TEXTURE_2D)

        # Sganciamo dalla pipeline la texture
        glBindTexture(GL_TEXTURE_2D, 0)

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
            layout(location = 1) in vec2 vertexUVcoords;

            // Dati in output, interpolati per ciascun frammento
            out vec2 UV;

            // Valori passati allo shader che rimangono costanti
            uniform mat4 MVP;

            void main(){
                // Calcolo della posizione del vertice in clip space: MVP * position
                gl_Position =  MVP * vec4(vertexPosition_modelspace, 1);

                // Coordinate UV del vertice.
                UV = vertexUVcoords;
            }
        """

        fragment_shader = """
            #version 330 core

            // Valori interpolati forniti dal vertex shader
            in vec2 UV;

            // Dati in output
            out vec3 color;

            // Valori costanti per tutta l'esecuzione
            uniform sampler2D textureSampler;

            void main(){
                color = texture2D( textureSampler, UV ).rgb;
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
        self.texture_sampler_uniform = glGetUniformLocation(self.program, "textureSampler")

        self.scale_matrix = self.get_scale_matrix()
        return True

    def draw(self, model, view, projection):
        if not self.shaders_ok:
            return

        # Calcolo la matrice model-view-projection
        # NOTA: fare attenzione all'ordine in cui compaiono!
        MVP = projection * view * model * self.scale_matrix

        # Impostiamo il programma che la GPU deve usare
        glUseProgram(self.program)

        # Associo la matrice MVP corrente al proprio uniform
        glUniformMatrix4fv(self.MVP_uniform, 1, GL_FALSE, glm.value_ptr(MVP))

        # Agganciamo il buffer dei vertici all'indice 0
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Agganciamo il buffer dei valori UV all'indice 1
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.texel_bufferId)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Associo il sampler della texture al proprio uniform
        glUniform1i(self.texture_sampler_uniform, 0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glDrawArrays(self.type, 0, self.length * 3)

        # Sgancio i due array dei vertici e degli UV
        glDisableVertexAttribArray(0)
        glDisableVertexAttribArray(1)

        # Disabilito il programma sulla GPU
        glUseProgram(0)

        # Sganciamo dalla pipeline i buffer
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # Sganciamo dalla pipeline la texture
        glBindTexture(GL_TEXTURE_2D, 0)

    def get_bbox(self):
        if not hasattr(self, 'bbox'):
            self.bbox = [numpy.min(self.vertici[::3]), numpy.max(self.vertici[::3]),
                         numpy.min(self.vertici[1::3]), numpy.max(self.vertici[1::3]),
                         numpy.min(self.vertici[2::3]), numpy.max(self.vertici[2::3])]
        return self.bbox

    def get_scale_matrix(self):
        bbox = self.get_bbox()
        width = abs(bbox[0]) + abs(bbox[1])
        height = abs(bbox[2]) + abs(bbox[3])
        depth = abs(bbox[4]) + abs(bbox[5])
        scale_factor = 1. / max(width, height, depth)
        return glm.scale(glm.vec3(scale_factor))
