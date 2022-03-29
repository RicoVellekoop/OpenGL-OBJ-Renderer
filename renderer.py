#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GL import shaders

from keyboardHandler import *
from mouseHandler import *
from scene import *
from camera import *

import glm  #   This library is used to handle Matrix and Vector math. This could be done with lists, but would be less efficient and more complicated.

#   This class will render a scene on the screen, and will handle most of the program like moving objects, and the inplementation of inputs.

def setShader():    #   This function will setup the right shaders, and will setup the vertex buffer
    	#  Define and compile the vertex shader
    	vsSource = '''#version 330
    	attribute vec3 pos;            //  The position of the current vertex
    	attribute vec3 normal;         //  The normal vector of the current vertex
    	attribute vec3 uv;             //  The uv coördinate of the current vertex

        uniform mat4 objectRotation;   //  The rotation matrix of the current object
    	uniform mat4 MVP;              //  The Model, View and Perspective matrices combined

    	out vec3 ourNormal;            //  The normal for each pixel on the screen
    	out vec2 uvFrag;               //  The uv coördinate for each pixel on the screen

    	void main() {
    		gl_Position =  MVP * vec4(pos, 1.0);  //  The position of each vertex is calculated by multipieing its homogenious coördinate with the MVP matrix

    		ourNormal = (vec4(normal, 1.0)*objectRotation).xyz;   //  Returns the normal for each pixel on the screen
    		uvFrag = vec2(uv.x, -uv.y);                           //  Returns the uv coördinate for each pixel on the screen. Note: the Y component is flipped in OpenGL
    	}
    	'''
    	vs = shaders.compileShader(vsSource, GL_VERTEX_SHADER)

        #  Define and compile the fragment shader
    	fsSource = '''#version 330
    	uniform bool isAlphaPass;          //  Defines if the shader should draw transparant pixels

    	uniform bool hasBumpmap;           //  Defines if the material has a bumpmap. Note: I have not inplemented bump maps
    	uniform bool hasTexture;           //  Defines if the material has a texture map
        uniform bool isSelected;           //  Defines if the object is selected

        uniform vec3 selectionColor;       //  Defines the color of selected objects
        uniform vec3 lightDirection;       //  Defines the direction the sunlight is coming from

    	uniform sampler2D difuseTexture;   //  Defines what diffuse texture to use
    	uniform sampler2D bumpMap;         //  Defines what bumpMap to use

    	in vec3 ourNormal; //  Get the fractional normal from the vertex shader
    	in vec2 uvFrag;    //  Get the fractional uv coördinate from the vertex shader

    	out vec4 fragColor;

    	void main() {
    		vec4 tex;
    		vec3 normalVec;

    		if(hasTexture){   //  If the material has a texture, get the right color from the texture, else pick white
    			tex = vec4(texture(difuseTexture, uvFrag).rgba);
    		}else{
    			tex = vec4(1.0,1.0,1.0,1.0);
    		}

    		normalVec = normalize(ourNormal); //  Normalise the normal for the lighting calculation later

            //  This program renders every thing twice. first it will only render all fully opaque objects, and then it will redraw any semitransparant parts on top of the last
            //  render this is to avoid not rendering behind transparant objects becouse of the z buffer while not having to make sure the image renders from back to front to avoid
            //  being able to look trought objects becouse of semitransparant textures
    		if(tex.a < 0.9999 && !isAlphaPass) discard;   //  This skips a pixel if it is semitransparant and it is rendering for the first time

            //  The following line will result in the color of the pixel on the screen. it is made by first calculating the difuse shading by taking the dot product between the
            //  normal vector and the light vector, and then multipieing it by 0.85 and adding 0.15 to simmulate shading.
            //  The resulting value is multiplied by the color from the texture map to apply the shading to the texture.
    		fragColor = vec4(min(1.0, 0.15+0.85*max(0,dot(normalVec, normalize(lightDirection))))*tex.rgb, tex.a);

            if(isSelected){ //  If the object is selected color of the object will be mixed with the selection color to indicate what object is selected
                fragColor = 0.8*fragColor + 0.2 * vec4(selectionColor, 1.0);
            }
    	}
    	'''
    	fs = shaders.compileShader(fsSource, GL_FRAGMENT_SHADER)

    	#  Combine the two shaders into a program
    	program = shaders.compileProgram(vs, fs)
    	glUseProgram(program)

    	#  Create a vertex buffer, and set the atrubutes to the right variables in the shader
    	buffer = glGenBuffers(1)
    	glBindBuffer(GL_ARRAY_BUFFER, buffer)

    	posAtribute = glGetAttribLocation(program, "pos")
    	glEnableVertexAttribArray(posAtribute)
    	glVertexAttribPointer(posAtribute, 3, GL_FLOAT, GL_FALSE, 36, None)

    	normalAtribute = glGetAttribLocation(program, "normal")
    	glEnableVertexAttribArray(normalAtribute)
    	glVertexAttribPointer(normalAtribute, 3, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(12))

    	uvAtribute = glGetAttribLocation(program, "uv")
    	glEnableVertexAttribArray(2)
    	glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 36, ctypes.c_void_p(24))
    	return program

class Renderer:
    def glSetup(self):  #   Set all information for OpenGL to the right vallues
        glutInit()
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow("Eindopdracht Rico Vellekoop".encode("ascii"))
        glClearColor(0.1, 0.1, 0.1, 1.0)

        #   Enable Z buffering to make sure the closest pixel is drawn on top
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glEnable(GL_CULL_FACE)

        #   Enable backface culling to only draw the outside of an object
        glCullFace(GL_FRONT)
        glFrontFace(GL_CW)
        glEnable(GL_BLEND);

        #   Define how to handle transparancy
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        #   Enable the stencil buffer used for object selection
        #   Object selection is implemented by writing the index of the object into the stencil buffer for each pixel of that object while drawing the image.
        #   This way if you click on the image you can look the value in the stencil buffer in the position where the mouse was when in clicked to get the index for that object.
        glEnable(GL_STENCIL_TEST)
        glStencilMask(0xFF)
        glClearStencil(0)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)

        #   Define what functions to use for displaying the image
        glutDisplayFunc(self.display)
        glutIdleFunc(self.display)

        #   Define what functions to use for user input
        glutKeyboardFunc(self.keyboard.buttonDown)
        glutMouseFunc(self.mouse.handleButton)
        glutPassiveMotionFunc(self.mouse.handlePosition)
        glutMotionFunc(self.mouse.handlePosition)

        #   Define the projection matrix
        self.projection = glm.perspective(glm.radians(45.0), self.width/self.height, 0.1, 1000.0)

    def display(self):
        dt = glutGet(GLUT_ELAPSED_TIME)/1000 - self.lastTime    #   Calculate the time passed since drawing the last image
        self.lastTime = glutGet(GLUT_ELAPSED_TIME)/1000

        self.processInput(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        if self.scene is not None:
            maskId = 1
            for mesh in self.scene.objects:
                glStencilFunc(GL_ALWAYS, maskId, 0xFF)  #   Select the right index for the object
                glUniform1i(glGetUniformLocation(self.shader, "isSelected"), int(maskId == self.scene.selected))    #   Tell the GPU if the current object is selected
                maskId += 1

                self.recalcMatrix(mesh.getMatrix(), mesh.rotationMatrix)     #   Calculate a MVP matrix with the Model matrix of the current object

                glUniform1i(glGetUniformLocation(self.shader, "isAlphaPass"), 0)    #   First render: opaque only
                for groupId in range(len(mesh.materials)):
                    mesh.materials[groupId].setActive(self.shader)  #   Load the current material to the GPU
                    glDrawArrays(GL_TRIANGLES, mesh.offset + mesh.mtlOffsets[groupId], mesh.mtlOffsets[groupId+1]-mesh.mtlOffsets[groupId])

                glUniform1i(glGetUniformLocation(self.shader, "isAlphaPass"), 1)    #   First render: transparancy
                for groupId in range(len(mesh.materials)):
                    mesh.materials[groupId].setActive(self.shader)  #   Load the current material to the GPU
                    glDrawArrays(GL_TRIANGLES, mesh.offset + mesh.mtlOffsets[groupId], mesh.mtlOffsets[groupId+1]-mesh.mtlOffsets[groupId])
        glFlush()




    def __init__(self, width, height):     #   Create a renderer object with default settings
        self.width = width
        self.height = height
        self.keyboard = KeyboardHandler()
        self.mouse = MouseHandler()

        self.glSetup()
        self.shader = setShader()
        self.setLightDirection(glm.vec3(1.0, -2.0, 0.5))
        self.setSelectionColor(glm.vec3(0.0, 0.68, 1.0))
        self.scene = None

        self.camera = Camera()

    def setSelectionColor(self, color): #   Set the color of selected object to a given color
        ptr = glm.value_ptr(color)
        glUniform3fv(glGetUniformLocation(self.shader, "selectionColor"), 1, ptr)

    def render(self):   #   Start rendering the image
        self.scene.loadGeometry()
        self.lastTime = glutGet(GLUT_ELAPSED_TIME)/1000
        glutMainLoop()

    def recalcMatrix(self, model, rotationMatrix):  #   Recalcuate the MVP matrix and load it on the GPU
        MatrixID = glGetUniformLocation(self.shader, "MVP")

        mvp = self.projection * self.camera.getMatrix() * model
        ptr = glm.value_ptr(mvp)
        glUniformMatrix4fv(MatrixID, 1, GL_FALSE, ptr)

        rotationID = glGetUniformLocation(self.shader, "objectRotation")    #   Also load the objects rotation matrix to rotate the object's normals to match the rotation

        objectRotation = rotationMatrix
        ptr = glm.value_ptr(objectRotation)
        glUniformMatrix4fv(rotationID, 1, GL_FALSE, ptr)

    def processInput(self, dt):
        scrollSpeed = 50.0      #   Difines a speed for scolling
        rotationSpeed = 300.0   #   Difines a speed for rotating things
        moveSpeed = 50.0        #   Difines a speed for moving things

        if self.mouse.leftBtn:  #   If the left mouse button is clicked
            #   Stop the editing of objects and revert to the old transformation
            if self.keyboard.moving:
                if self.keyboard.oldVec is not None:
                    self.scene.getSelected().position = self.keyboard.oldVec
                self.keyboard.stopEdit()
                self.setSelectionColor(glm.vec3(0.0, 0.68, 1.0))

            if self.keyboard.scaling:
                if self.keyboard.oldVec is not None:
                    self.scene.getSelected().objScale = self.keyboard.oldVec
                self.keyboard.stopEdit()
                self.setSelectionColor(glm.vec3(0.0, 0.68, 1.0))

            if self.keyboard.rotating:
                if self.keyboard.oldVec is not None:
                    self.scene.getSelected().rotationMatrix = self.keyboard.oldVec
                self.keyboard.stopEdit()
                self.setSelectionColor(glm.vec3(0.0, 0.68, 1.0))

            #   Select the object under the cursor if there is one
            self.scene.selected = glReadPixels(self.mouse.x, self.height - self.mouse.y - 1, 1, 1, GL_STENCIL_INDEX, GL_UNSIGNED_INT, None)

        if self.mouse.rightBtn: #   If the Right mouse button is clicked
            #   Stop editing the selected object, but keep the new transformation
            if self.keyboard.moving or self.keyboard.scaling or self.keyboard.rotating:
                self.keyboard.stopEdit()
                self.setSelectionColor(glm.vec3(0.0, 0.68, 1.0))
            #   Deselect all objects
            self.scene.selected = 0

        if not self.keyboard.scaling:
            if self.mouse.scrollUp:
                self.zoomCamera("In", scrollSpeed, dt)  #   Zoom the camera in if you are not scaling an object

            if self.mouse.scrollDown:
                self.zoomCamera("Out", scrollSpeed, dt) #   Zoom the camera out if you are not scaling an object

        if self.mouse.rotating: #   Rotate the camera
            self.rotateCamera(rotationSpeed)

        if self.mouse.moving:   #   Move the camera
            self.moveCamera(moveSpeed)

        if self.keyboard.orbit: #   Make the camera orbit around the focus point
            self.camera.camZRot += 15.0*dt

        if self.scene.selected > 0:     #   Transform the selected object if a transformation is enabled
            if self.keyboard.moving:
                self.moveObject(moveSpeed)

            if self.keyboard.scaling:
                self.scaleObject()

            if self.keyboard.rotating:
                self.rotateObject(rotationSpeed)

    def rotateCamera(self, speed):  #   Rotate the camera by the distance the mouse has moved since last frame
        self.camera.rotate(speed*(self.mouse.x - self.mouse.lastX)/self.width, speed*(self.mouse.y - self.mouse.lastY)/self.height)
        self.mouse.lastX = self.mouse.x
        self.mouse.lastY = self.mouse.y

    def moveCamera(self, speed):    #   Move the camera by the distance the mouse has moved since last frame
        #   The movement position is calculated first to account for the rotation of the camera
        movementPos = glm.rotate(glm.vec3(0, -speed*(self.mouse.x - self.mouse.lastX)/self.width, speed*(self.mouse.y - self.mouse.lastY)/self.height), glm.radians(self.camera.camYRot), glm.vec3(0.0, 1.0, 0.0))
        movementPos = glm.rotate(movementPos, glm.radians(self.camera.camZRot), glm.vec3(0.0, 0.0, 1.0))
        self.camera.move(movementPos)

        self.mouse.lastX = self.mouse.x
        self.mouse.lastY = self.mouse.y

    def zoomCamera(self, direction, speed, dt): #   Zoom the camera in or out
        if direction == "In":
            self.camera.camDistance = max(0.001, self.camera.camDistance - (speed*dt))
            self.mouse.scrollUp = False
        if direction == "Out":
            self.camera.camDistance = self.camera.camDistance + (speed*dt)
            self.mouse.scrollDown = False

    def moveObject(self, speed):    #   Move the selected object by the distance the mouse has moved since last frame
        if self.keyboard.oldVec is None:
            self.mouse.lastX = self.mouse.x
            self.mouse.lastY = self.mouse.y
            self.keyboard.oldVec = self.scene.getSelected().position    #   Saves the old position the first frame this transformation is selected
            self.setSelectionColor(glm.vec3(1.0, 0.65, 0.0))            #   Sets the selection color to Orange to indicate Moving objects is selected

        #   Moving objects is done allmost the same way it is done for the camera
        movementPos = glm.rotate(glm.vec3(0, speed*(self.mouse.x - self.mouse.lastX)/self.width, -speed*(self.mouse.y - self.mouse.lastY)/self.height), glm.radians(self.camera.camYRot), glm.vec3(0.0, 1.0, 0.0))
        movementPos = glm.rotate(movementPos, glm.radians(self.camera.camZRot), glm.vec3(0.0, 0.0, 1.0))
        self.scene.getSelected().move(movementPos)

        self.mouse.lastX = self.mouse.x
        self.mouse.lastY = self.mouse.y

    def rotateObject(self, speed):
        if self.keyboard.oldVec is None:
            self.keyboard.oldVec = self.scene.getSelected().rotationMatrix  #   Saves the old rotation the first frame this transformation is selected
            self.setSelectionColor(glm.vec3(0.5, 0.0, 1.0))                 #   Sets the selection color to Purple to indicate Rotating objects is selected
            self.mouse.lastX = self.mouse.x
            self.mouse.lastY = self.mouse.y

        #   The difference from the x coördinate of the mouse is rotated the Y axis of the screen translated to 3d space in regards to the camera rotation
        self.scene.getSelected().rotate(speed*(self.mouse.x - self.mouse.lastX)/self.width, self.camera.getYAxis())
        #   The difference from the y coördinate of the mouse is rotated the X axis of the screen translated to 3d space in regards to the camera rotation
        self.scene.getSelected().rotate(speed*(self.mouse.y - self.mouse.lastY)/self.width, self.camera.getXAxis())
        self.mouse.lastX = self.mouse.x
        self.mouse.lastY = self.mouse.y

    def scaleObject(self):  #   Scale by scrolling up and down
        if self.keyboard.oldVec is None:
            self.keyboard.oldVec = self.scene.getSelected().objScale    #   Saves the old scale the first frame this transformation is selected
            self.setSelectionColor(glm.vec3(0.0, 1.0, 0.0))             #   Sets the selection color to Green to indicate Scaling objects is selected

        if self.mouse.scrollUp:     #   If the user scrolls up the selected object is scaled by 1.1
            self.mouse.scrollUp = False
            self.scene.getSelected().scale(1.1)

        if self.mouse.scrollDown:   #   If the user scrolls up the selected object is scaled by 0.9
            self.mouse.scrollDown = False
            self.scene.getSelected().scale(0.9)

    def setLightDirection(self, vec):   #   Load the a vector with the direction of the sun light to the GPU
        ptr = glm.value_ptr(vec)
        glUniform3fv(glGetUniformLocation(self.shader, "lightDirection"), 1, ptr)
