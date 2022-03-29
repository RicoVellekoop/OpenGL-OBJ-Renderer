#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

from OpenGL.GL import *

#   This class contains all information about the material of an object
class Material:
    def __init__(self, description):    #   This makes a material object using the lines from the .MTL corrosponding to the material
        self.name = ""

        self.hasBumpmap = False     #   Note: I originaly wanted to implement normal maps, but this proved to be way harder than expected, so for now i decided i won't implement this
        self.hasTexture = False

        for line in description:    #   Reads all lines and stores the variables it needs for my program
            if line.strip()[:6] == "newmtl":
                self.name = line.strip()[7:].rstrip("\n")
            elif line.strip()[:6] == "map_Kd":
                self.hasTexture = line.strip()[7:].rstrip("\n")
            elif line.strip()[:8] == "map_Bump":
                self.hasBumpmap = line.strip()[9:].rstrip("\n")

    def setActive(self, program):   #   Sends all information about the material to the GPU so the material can be applied in the shader
        if self.hasTexture != False:
            glUniform1i(glGetUniformLocation(program, "hasTexture"), 1)
            glUniform1i(glGetUniformLocation(program, "difuseTexture"), self.hasTexture)
        else:
            glUniform1i(glGetUniformLocation(program, "hasTexture"), 0)
        if self.hasBumpmap != False:
            glUniform1i(glGetUniformLocation(program, "hasBumpmap"), 1)
            glUniform1i(glGetUniformLocation(program, "bumpMap"), self.hasBumpmap)
        else:
            glUniform1i(glGetUniformLocation(program, "hasBumpmap"), 0)
