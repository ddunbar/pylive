"""
This module implements the window abstraction exposed to the PyLive API.
"""

import os
import sys
import time

from OpenGL.GLUT import *
from OpenGL.GL import *

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

        self.last_module_check_time = -1
        self.non_autoreload_modules = {}
        self.module_time_cache = {}

    def run(self):
        glutMainLoop()

    def iter_modules_to_watch(self):
        for module in sys.modules.values():
            path = getattr(module, '__file__', None)
            if module not in self.non_autoreload_modules and \
                   path is not None and \
                   os.path.isfile(path):
                if os.path.splitext(path)[1] in ['.pyc', '.pyo', '.pyd']:
                    path = path[:-1]
                yield (module, path)

    def set_autoreload(self, value):
        self.autoreload = value

    def set_module(self, module_path):
        # Record the current module set.
        self.non_autoreload_modules = set(sys.modules.values())

        # Load the initial module.
        self.module_path = module_path
        self.module = __import__(module_path, fromlist=['register_pylive'])

        # Initialize the module cache.
        for module,path in self.iter_modules_to_watch():
            mtime = os.stat(path).st_mtime
            self.module_time_cache[path] = mtime

        # Create the actual proxy.
        self.proxy = self.module.register_pylive(self)

    def check_if_needs_reload(self):
        for module,path in self.iter_modules_to_watch():
            mtime = os.stat(path).st_mtime
            if mtime != self.module_time_cache.get(path):
                return True

    def reload_module(self):
        print >>sys.stderr, "pylive: reloading module..."

        # Reload all the modified modules (except the main module).
        for module,path in self.iter_modules_to_watch():
            mtime = os.stat(path).st_mtime
            if mtime != self.module_time_cache.get(path):
                self.module_time_cache[path] = mtime
                reload(module)

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
        current_time = time.time()
        if current_time - self.last_module_check_time > .1:
            if self.check_if_needs_reload():
                self.reload_module()
            self.last_module_check_time = current_time

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
