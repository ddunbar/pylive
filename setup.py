import pylive
import os

from setuptools import setup, find_packages

# setuptools expects to be invoked from within the directory of setup.py, but it
# is nice to allow:
#   python path/to/setup.py install
# to work (for scripts, etc.)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

setup(
    name = "PyLive",
    version = pylive.__version__,

    author = pylive.__author__,
    author_email = pylive.__email__,
    license = 'BSD',

    description = "Python OpenGL LiveCoding environment",
    keywords = 'opengl livecoding',
    long_description = """\
*PyLive*
++++++++

About
=====

*PyLive* is a livecoding environment for Python + OpenGL.
""",

    packages = find_packages(),

    entry_points = {
        'console_scripts': [
            'pylive = pylive.app:main',
            ],
        },

    install_requires=['Flask', 'PyOpenGL', 'PyOpenGL_accelerate'],
)
