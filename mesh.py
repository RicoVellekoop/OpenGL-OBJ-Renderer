#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

from material import *

from OpenGL.GL import *

import glm      #   This library is used to handle Matrix and Vector math. This could be done with lists, but would be less efficient and more complicated.
from PIL import Image

class Mesh:     #   This class contains the data for each of the vertecies of a mesh, the materials used in the mesh, and information about their transformations
    def __init__(self, verts, mtlOffsets, materials, vertexOffset):
        self.verts = verts              #   Stores all data about each vertex
        self.mtlOffsets = mtlOffsets    #   This list contains a index for the first vertex of each material group
        self.materials = materials      #   This list contains all materials in the mesh

        self.offset = vertexOffset      #   The offset of the first vertex in the arrayBuffer on the gpu

        self.position = glm.vec3(0.0)
        self.objScale = glm.vec3(1.0)
        self.rotationMatrix = glm.mat4(1.0)

    @classmethod
    def loadMTL(cls, path):     #   This method reads a .MTL file and returns a list with all materials described in the file
        #   Stores the path to the folder of the file. This way the right image files can be loaded while the model can be in a different folder than the .py file
        currentFolder = "".join([folder + "/" for folder in path.split('/')[0:-1]])

        foundFirstMtl = False

        materials = []
        textures = []

        with open(path, "r") as file:   #   Reads each line of the mtl file and checks if it finds a keyword
            mtlDescription = []
            for line in file.readlines():
                if line[:6] == "newmtl":    #   This keyword signals the start of a materials
                    if foundFirstMtl:       #   If it has found a file before the stored description of the last material is added to the materials list as a material object
                        materials.append(Material(mtlDescription))
                    else:
                        foundFirstMtl = True
                    mtlDescription = []
                elif line.strip()[:6] == "map_Kd":      #   A line with this keyword contains the path to the defuse(texture) map of a material
                    textures.append(line.strip()[7:].rstrip("\n"))
                elif line.strip()[:8] == "map_Bump":    #   A line with this keyword contains the path to the normal map of a material
                    textures.append(line.strip()[9:].rstrip("\n"))
                mtlDescription.append(line)     #   Stores every line about one material to make a material object later
            materials.append(Material(mtlDescription))

        textures = list(set(textures))              #   Remove duplicate file names from the list to avoid loading the same image twice

        #   Load all images in the GPU memory to use in the shaders later
        textureIDs = glGenTextures(len(textures))
        for textureNr in range(len(textures)):
            img = Image.open(currentFolder + textures[textureNr]).convert('RGBA')
            glActiveTexture(GL_TEXTURE0 + textureIDs[textureNr])
            glBindTexture(GL_TEXTURE_2D, textureIDs[textureNr])
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.size[0], img.size[1], 0, GL_RGBA, GL_UNSIGNED_BYTE, img.tobytes())
            glGenerateMipmap(GL_TEXTURE_2D);    #   Generate mipmap's to avoid texture distortion when zooming out

        #   Links the right id for each texture to each material
        for mtl in materials:
            if mtl.hasTexture != False:
                mtl.hasTexture = textureIDs[textures.index(mtl.hasTexture)]
            if mtl.hasBumpmap != False:
                mtl.hasBumpmap = textureIDs[textures.index(mtl.hasBumpmap)]
        return materials

    @classmethod    #   This method creates a mesh object out of a .OBJ file
    def loadOBJ(cls, path, vertexOffset):
        currentFolder = "".join([folder + "/" for folder in path.split('/')[0:-1]]) #   Stores the folder of the .OBJ file to find the .MTL file later
        verts = []
        uvCords = []
        normals = []
        finalList = []      #   This list will become a list of vertex data. The order of the data is: position, normal vector, uv coördinate
        materialOffset = []
        materialName = []

        hasNormals = False

        with open(path, "r") as file:   #   Reads each line of the mtl file and checks if it finds a keyword
            faceCounter = 0
            for line in file.readlines():
                if line[:6] == "mtllib":    #   A line with this keyword contains a path to the .MTL file
                    mtl = Mesh.loadMTL(currentFolder + line[7:].rstrip("\n"))
                if line[:6] == "usemtl":    #   A line with this keyword signals the material the next vertecies are drawn with
                    materialName.append(line[7:].rstrip("\n"))
                    materialOffset.append(faceCounter*3)
                elif line[0] == "v":
                    if line[1] == "t":      #   The keyword "vt" signals a uv(texture) cordinate
                        uv = [float(i) for i in line[3:].split(' ') if i.strip()]
                        if len(uv) == 2:
                            uv.append(0)
                        uvCords.append(glm.vec3(uv))
                    elif line[1] == "n":    #   The keyword "vn" signals a normalVector
                        #   Note: the normal is rotated, becouse in my program Z is up in 3d space, while most .OBJ files consider Y the upwards axis
                        normals.append(glm.rotate(glm.radians(90), glm.vec3(0,0,1)) * glm.rotate(glm.radians(90), glm.vec3(1,0,0)) * glm.vec3([float(i) for i in line[3:].split(' ') if i.strip()]))
                        if not hasNormals:
                            hasNormals = True
                    else:   #   The "v" keyword signals a vertex coördinate
                        #   Note: the vertex is rotated, becouse in my program Z is up in 3d space, while most .OBJ files consider Y the upwards axis
                        verts.append(glm.rotate(glm.radians(90), glm.vec3(0,0,1)) * glm.rotate(glm.radians(90), glm.vec3(1,0,0)) * glm.vec3([float(i) for i in line[2:].split(' ') if i.strip()]))
                elif line[0] == "f":    #   The "f" keyword signals a face of the object
                    #   In an .OBJ file a face is defined by an f followed by the the information of the vertecies seperated by a space. Each vertex is represented as
                    #   a/b/c in which a, b, and c are three indexes of their the data listed before it.
                    #   The index at the place of a is the index for the vertex coördinate of that vertex.
                    #   The index at the place of b is the index for the texture coördinate of that vertex.
                    #   The index at the place of c is the index for the normal vector of that vertex, this one is optional.
                    #   The next line splits a line with a face into a list with all vertecies at list of the indexes named above
                    face = [i.split('/') for i in line[2:].rstrip("\n").split(' ') if i.strip()]
                    #   Note: the faceCounter doesn't get incremented by 1 because tiangulation is preformed later which will increase the face count according to the amout of vertecies
                    #   in the face in the .OBJ file
                    faceCounter += len(face) - 2
                    #   Triangulation is done to make it easier to draw the model later. This is done by looping trought the list from the second vertex to the second last and making faces
                    #   between the current vertex, the next vertex and the fist vertex in the list.
                    for trig in range(1, len(face)-1):
                        #   First the data of the first vertex is added to the list
                        finalList.append(verts[int(face[0][0])-1])
                        if not hasNormals:
                            #   If there are no normal vectors found in the file the program will calculate the normals for each face. These normals will result in flat shading
                            #   instead of smooth shading to the normals from the .OBJ file are prefered.
                            normal = glm.cross((verts[int(face[trig][0])-1]-verts[int(face[0][0])-1]), (verts[int(face[trig + 1][0])-1]-verts[int(face[0][0])-1]))
                            finalList.append(normal)
                        else:
                            finalList.append(normals[int(face[0][2])-1])
                        finalList.append(uvCords[int(face[0][1])-1])
                        for vert in range(2):   #   Then the data of other two vertexes are added to the list
                            finalList.append(verts[int(face[trig + vert][0])-1])
                            if not hasNormals:
                                finalList.append(normal)
                            else:
                                finalList.append(normals[int(face[trig + vert][2])-1])
                            finalList.append(uvCords[int(face[trig + vert][1])-1])
        materialOffset.append(faceCounter*3)

        #   Sorts the generated materials in the order found in the .OBJ file to make sure the right materials are used with the right vertecies
        mtlNames = [m.name for m in mtl]
        mtlList = [mtl[mtlNames.index(name)] for name in materialName]

        return cls(finalList, materialOffset, mtlList, vertexOffset)

    def scale(self, vec):   #   Scales the object
        self.objScale = self.objScale * vec

    def rotate(self, angle, axis):  #   Rotates the object
        self.rotationMatrix = glm.rotate(glm.radians(angle), axis) * self.rotationMatrix

    def move(self, vec):    #   Moves the object
        self.position = self.position + vec

    def getMatrix(self):    #   Calculates the translation matrix and scalings matrix, and multiplies them with the rotation matrix to make the Model matrix
        return glm.translate(glm.mat4(), self.position) * glm.scale(self.objScale) * self.rotationMatrix
