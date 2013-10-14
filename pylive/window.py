"""
This module implements the window abstraction exposed to the PyLive API.
"""

from OpenGL.GLUT import *
from OpenGL.GL import *
import time

class WindowProxy(object):
    def __init__(self, window):
        self.window = window

    def on_draw(self):
        pass

class Window(object):
    def __init__(self, name, width, height):
        self.width = width
        self.height = height

        # We simply assume only one Window is ever created.
        glutInit([])
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutCreateWindow(name)

        glClearColor(1, 1, 1, 1)

        glutDisplayFunc(self.display_callback)
        glutIdleFunc(self.idle_callback)
        glutReshapeFunc(self.reshape_callback)
        glutSpecialFunc(self.special_callback)

        self.proxy = WindowProxy(self)
        self.module = None
        self.module_path = None

        self.redisplay = False

    def run(self):
        glutMainLoop()

    def set_module(self, module_path):
        # Load the initial module.
        self.module_path = module_path
        self.module = __import__(module_path, fromlist=['register_pylive'])

        # Create the actual proxy.
        self.proxy = self.module.register_pylive(self)

    def reload_module(self):
        # Reload the primary module.
        reload(self.module)

        self.module = __import__(self.module_path, fromlist=['register_pylive'])
        self.proxy = self.module.register_pylive(self, self.proxy)

        # Force an update.
        self.update()

    ###
    # Public API

    def update(self):
        self.redisplay = True

    ###
    # GLUT Callbacks

    def idle_callback(self):
        if self.redisplay:
            glutPostRedisplay()
            self.redisplay = False
        time.sleep(0.001)

    def special_callback(self, key, x, y):
        print ('special', chr(key), x, y)
        if chr(key) == 'r':
            self.reload_module()

    def reshape_callback(self, width, height):
        self.width = width
        self.height = height

    def display_callback(self):
        glViewport(0, 0, self.width, self.height)

        glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	glOrtho(0, self.width, 0, self.height, -1, 1)
	
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        self.proxy.on_draw()

        glutSwapBuffers()
