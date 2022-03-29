#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

from mesh import *

#   This class is used to store multiple objects and some data about them
class Scene:
    def __init__(self):
        self.vertexOffset = 0
        self.objects = []
        self.selected = 0

    def importObject(self, path):   #   This functions adds an object to a scene. it also keeps track of how many faces are in each object to make sure the materials are used on the right object
        mesh = Mesh.loadOBJ(path, self.vertexOffset)
        self.vertexOffset = self.vertexOffset + int(len(mesh.verts)/3)
        self.objects.append(mesh)

    def loadGeometry(self): #   This function loads all the vertecies from the objects in the scene to the GPU
        vertexArray = []
        for mesh in self.objects:
            vertexArray.extend(mesh.verts)

        arr = glm.array(vertexArray)
        glBufferData(GL_ARRAY_BUFFER, arr.nbytes, arr.ptr, GL_STATIC_DRAW)

    def getSelected(self):  #   Returns the selected object, Note: int(self.selected)-1 is used, the default stencil value is 0, so all values are shifted by +1
        return self.objects[int(self.selected)-1]
