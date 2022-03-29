#   Eindopdracht Computer Graphics 2022
#   Rico Vellekoop (1001564)

#   Controls:
#
#   Middle Mouse button         = Rotate camera
#   Shift + Middle Mouse button = Move camera
#
#   Left Mouse button   = Revert transformations & select object
#   Right Mouse button  = Deselect objects
#
#   o   = Toggle orbit camera
#
#   While an object is selected:
#   g   = Move mode
#   r   = Rotation mode
#   s   = Scale mode

#   Edit Modes:
#   There are three modes which can be used to transform objects. These modes can be entered by selecting a object and pressing the corresponding keybind. Right clicking will deselect the object,
#   and the object will keep the new transformation, and left clicking will revert the transformation to the previous one. The available modes are:
#   Move mode (keybind = g) indicated by a Orange tint on the selected object. In this mode you can move the selected object by moving the mouse
#   Rotation mode (keybind = r) indicated by a Purple tint on the selected object. In this mode you can rotate the selected object by moving the mouse
#   Scale mode (keybind = s) indicated by a Green tint on the selected object. In this mode you can scale the selected object by scrolling up or down with the mouse wheel

from renderer import *
from scene import*

renderer = Renderer(1280, 720) #   You can set your resolution here. Note: Resizing the window will break the object selection
scene = Scene()
renderer.scene = scene

#   These lines are used to load objects into the scene
scene.importObject("models/Coconut/coconut.obj")
scene.importObject("models/Bayonetta/bayo.obj")

renderer.render()
