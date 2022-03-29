#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

from OpenGL.GLUT import *

class MouseHandler: #   This class handles all inputs from the mouse
    def __init__(self):
        self.x = 0
        self.y = 0

        self.lastX = 0
        self.lastY = 0

        self.rotating = False
        self.moving = False

        self.leftBtn = False
        self.rightBtn = False
        self.scrollUp = False
        self.scrollDown = False

    def handleButton(self, button, state, x, y):    #   This function is called when a mousepress is detected, and executes the code corrosponding to the key
        #   Note: state is False when the button is pressed. This is why I use not bool(state) most of the time to invert it so that it is True when the button is pressed.
        if button == 0:     #   Left mouse button
            self.leftBtn = not bool(state)  #   set variable to True if the button is pressed down, and false if it is released
            self.lastX = x
            self.lastY = y
            self.x = x
            self.y = y

        elif button == 2:   #   Right mouse button
            self.rightBtn = not bool(state) #   set variable to True if the button is pressed down, and false if it is released

        elif button == 1:   #   Scrollwheel pressed down
            if glutGetModifiers() == 0:     #   If no modifiers are pressed the mouse will be able to rotate the camera
                self.rotating = not bool(state)
                self.moving = False
            elif glutGetModifiers() == GLUT_ACTIVE_SHIFT:   #   If shift is held the mouse will be able to move the camera
                self.moving = not bool(state)
                self.rotating = False

            if not bool(state) == True: #   Resets the lastX and Y so the camera won't jump when starting to rotate or move the camera
                self.lastX = x
                self.lastY = y
                self.x = x
                self.y = y

        elif button == 3 and not bool(state) == False:  #   Scrollwheel moved up
            self.scrollUp = True

        elif button == 4 and not bool(state) == False:  #   Scrollwheel moved down
            self.scrollDown = True

    def handlePosition(self, x, y): #   This function is called by OpenGL, and keeps track of where the mouse is on the screen
        self.x = x
        self.y = y
