# OpenGL-OBJ-Renderer
This program was created as a part of a Computer Graphics course for the study Applied Computer Science at the Rotterdam University of Applied Sciences.
This program is a basic .obj file viewer with basic material support for difuse textures using .mtl files.
It can be used to load 3D meshes from a .obj file, which can be rotated, scaled, and moved across the scene.
The program also loads normal maps for detailed shadows, but I haven't applied them using shaders, becouse I was still figuring out what would be the right way to implement them.

<h3>Controls</h3>
  Middle Mouse button         = Rotate camera<br>
  Shift + Middle Mouse button = Move camera<br>

  Left Mouse button   = Revert transformations & select object<br>
  Right Mouse button  = Deselect objects<br>

  o   = Toggle orbit camera<br>

  While an object is selected:<br>
  g   = Move mode<br>
  r   = Rotation mode<br>
  s   = Scale mode<br>

<h3>Example Images</h3>

![Example1](ExampleImages\Example1.png)
![Example2](ExampleImages\Example2.png)
