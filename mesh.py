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
        self.normali = data[:, 2:5].reshape(-1)

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

        # Ripetiamo tutto per i dati delle normali
        self.normal_bufferId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_bufferId)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.normali), self.normali, GL_STATIC_DRAW)

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
            layout(location = 2) in vec3 vertexNormal_modelspace;

            // Dati in output, interpolati per ciascun frammento
            out vec2 UV;

            out vec3 vertexPosition_worldspace;
            out vec4 vertexToCamera_cameraspace;
            out vec4 normal_cameraspace;

            // Valori passati allo shader che rimangono costanti
            uniform mat4 MVP;

            uniform mat4 M;
            uniform mat4 V;

            void main(){
                // Calcolo della posizione del vertice in clip space: MVP * position
                gl_Position =  MVP * vec4(vertexPosition_modelspace, 1);

                // Coordinate UV del vertice.
                UV = vertexUVcoords;

                // Posizione del vertice in spazio mondo
                vertexPosition_worldspace = ( M * vec4(vertexPosition_modelspace, 1) ).xyz;
                // Vettore che va dal vertice alla camera, in camera space
                // (in camera space, la camera è nell'origine).
                vertexToCamera_cameraspace = normalize(vec4(0,0,0,1) - V * M * vec4(vertexPosition_modelspace, 1));
                // Normale del vertice, in camera space
                // Corretto solo se la matrice di model non scala il modello!
                // Usare l'inversa trasposta altrimenti.
                normal_cameraspace = normalize( V * M * vec4(vertexNormal_modelspace, 0) );
            }
        """

        fragment_shader = """
            #version 330 core

            // Valori interpolati forniti dal vertex shader
            in vec2 UV;

            in vec3 vertexPosition_worldspace;
            in vec4 vertexToCamera_cameraspace;
            in vec4 normal_cameraspace;

            // Dati in output
            out vec4 color;

            // Valori costanti per tutta l'esecuzione
            uniform sampler2D textureSampler;

            // Struttura che rappresenta il materiale dell'oggetto
            struct Material {
                vec4  color;
                float ambientIntensity;
                vec3  specularColor;
                float specularIntensity;
                float flareIntensity;
            };

            // Struttura che rappresenta una luce
            struct Light {
                vec3  color;
                vec4  directionOrPosition;
                float intensity;
            };

            //uniform Material material = Material(vec4(1,1,1,1), 10, vec3(255,153,0)/255., 2, 2);
            uniform Material material = Material(vec4(1,1,1,1), 0.15, vec3(255,153,0)/255., 0.08, 3);

            //uniform Light light1 = Light(vec3(1,1,1), vec4(-3,0,0,1), 10);
            uniform Light light1 = Light(vec3(1,1,1), vec4(1,0,0.5,0), 1.6);

            vec4 computeLight(Light light, in vec4 materialDiffuseColor){
                // Normale interpolata del frammento, in camera space
                vec4 n = normalize( normal_cameraspace );

                // Direzione della luce
                // w = 0 è una direzione, w = 1 è una posizione
                // light.directionOrPosition.w * vertexToCamera_cameraspace + V * light.directionOrPosition;
                vec4 l = normalize( (light.directionOrPosition.w * vertexToCamera_cameraspace + light.directionOrPosition) );
                // Direzione interpolata dal frammento alla camera
                vec4 E = normalize(vertexToCamera_cameraspace);
                // Direzione nella quale il frammento riflette la luce
                vec4 R = normalize( reflect(-l, n) );

                // Distanza dalla luce
                float distance = length( light.directionOrPosition.xyz - vertexPosition_worldspace );
                // Se la luce è direzionale la distanza è 1
                distance = abs(light.directionOrPosition.w - 1) + distance * distance * light.directionOrPosition.w;

                vec3 materialAmbientColor = (light.intensity * material.ambientIntensity) * materialDiffuseColor.rgb;
                vec3 materialSpecularColor = material.specularIntensity * material.specularColor;

                // Coseno dell'angolo formato dalla normale e dalla direzione della luce, nel range 0 : 1
                //	- la luce è sulla verticale del triangolo -> 1
                //	- la luce è parallela alla superficie del triangolo o dietro -> 0
                float cosTheta = max( 0.0, dot(n, l) );

                // Coseno dell'angolo formato dalla direzione della camera e dalla direzione di riflessione, nel range 0 : 1
                //	- La camera guarda verso il riflesso -> 1
                //	- La camera guarda altrove -> 0
                float cosAlpha = max( 0.0, dot( E, R ) );

                vec4 finalColor = vec4( clamp(
                    // Ambient: simula la luce indiretta
                    materialAmbientColor / distance +

                    // Diffuse: "colore" dell'oggetto
                    materialDiffuseColor.rgb * light.color * (light.intensity + 0.015) * cosTheta / distance +

                    // Specular: riflesso dell'oggetto
                    materialSpecularColor * light.color * light.intensity * pow(cosAlpha, material.flareIntensity ) / distance
                    , 0, 1 ), materialDiffuseColor.a * material.color.a);

                return finalColor;
            }

            void main(){
                vec4 materialDiffuseColor = texture2D( textureSampler, UV );
                color = computeLight(light1, materialDiffuseColor);
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
        self.M_uniform = glGetUniformLocation(self.program, "M")
        self.V_uniform = glGetUniformLocation(self.program, "V")
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

        # Associo le matrici M e V correnti al proprio uniform
        glUniformMatrix4fv(self.M_uniform, 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(self.V_uniform, 1, GL_FALSE, glm.value_ptr(view))

        # Agganciamo il buffer dei vertici all'indice 0
        glEnableVertexAttribArray(0)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_bufferId)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Agganciamo il buffer dei valori UV all'indice 1
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.texel_bufferId)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Agganciamo il buffer delle normali all'indice 2
        glEnableVertexAttribArray(2)
        glBindBuffer(GL_ARRAY_BUFFER, self.normal_bufferId)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, None)

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
        glDisableVertexAttribArray(2)

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
