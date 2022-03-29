#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

import glm      #   This library is used to handle Matrix and Vector math. This could be done with lists, but would be less efficient and more complicated.

#   This class contains information about the camera in 3d space. This camera is placed a cirtain distance form a point and can be rotaded anound it.
class Camera:
    def __init__(self):     #   Creates a camera with the default settings
        self.camDistance = 20
        self.camZRot = 0
        self.camYRot = 0
        self.camPos = glm.vec3(1,0,0)
        self.focusPos = glm.vec3(0,0,0)

    def rotate(self, zRot, yRot):   #   Rotates the camera around a focus point
        self.camZRot = self.camZRot - zRot
        self.camYRot = min(max(self.camYRot - yRot, -89.9999),89.9999)

    def move(self, vec):    #   Moves the focus point
        self.focusPos = self.focusPos + vec

    def getMatrix(self):    #   Returs the View matrix of the camera
        #   Calculate the current possition of the camera
        self.camPos = glm.rotate(glm.vec3(self.camDistance, 0.0, 0.0), glm.radians(self.camYRot), glm.vec3(0.0, 1.0, 0.0))
        self.camPos = self.focusPos + glm.rotate(self.camPos, glm.radians(self.camZRot), glm.vec3(0.0, 0.0, 1.0))

        return glm.lookAt(self.camPos, self.focusPos, glm.vec3(0,0,1))  #   Create a view matrix for a camera placed at camPos, and looking at focusPos and returns it

    def getYAxis(self): #   returns the relative y-axis from the screen in the 3d scene
        return glm.rotate(glm.rotate(glm.vec3(0.0, 0.0, -1.0), glm.radians(self.camYRot), glm.vec3(0.0, 1.0, 0.0)), glm.radians(self.camZRot), glm.vec3(0.0, 0.0, 1.0))

    def getXAxis(self): #   returns the relative x-axis from the screen in the 3d scene
        return glm.rotate(glm.rotate(glm.vec3(0.0, -1.0, 0.0), glm.radians(self.camYRot), glm.vec3(0.0, 1.0, 0.0)), glm.radians(self.camZRot), glm.vec3(0.0, 0.0, 1.0))
