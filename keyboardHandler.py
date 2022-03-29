#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

import glm      #   This library is used to handle Matrix and Vector math. This could be done with lists, but would be less efficient and more complicated.

class KeyboardHandler:  #   This class is used to handle all inputs from the keyboard.
    def __init__(self):     #   Creates an object with the default settings
        self.orbit = False

        self.moving = False
        self.scaling = False
        self.rotating = False

        # self.editVec = glm.vec3(0.0)
        self.oldVec = None

    def buttonDown(self, key, x, y):    #   This function is called when a keypress is detected, and executes the code corrosponding to the key
        if key == b'g':         #   If "g" is pressed you can move the selected object
            self.stopEdit()
            self.moving = True
        elif key == b's':       #   If "s" is pressed you can scale the selected object
            self.stopEdit()
            self.scaling = True
        elif key == b'r':       #   If "r" is pressed you can rotate the selected object
            self.stopEdit()
            self.rotating = True
        elif key == b'o':       #   If "o" is pressed the camera will toggle between orbiting around the focus point, and not orbiting
            self.orbit = not self.orbit

    def stopEdit(self):     #   sets all variables for editing objects back to the default ones to stop editing objects
        self.moving = False
        self.scaling = False
        self.rotating = False

        self.oldVec = None
