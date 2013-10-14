"""
This module implements the PyLive REST API.
"""

import logging
import logging.handlers
import os
import sys
import threading

import flask
import api
import window

class App(flask.Flask):
    def __init__(self, name):
        super(App, self).__init__(name)

        # Register the API blueprint.
        self.register_blueprint(api.blueprint)

        # Create the PyLive window.
        self.window = window.Window('PyLive',
                                    x=850, y=0,
                                    width=600, height=1024)

###
# Server Entrypoint

def run_pylive(module_path):
    app = App(__name__)

    # Setup the base logger.
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger("octorack")
    logger.setLevel(logging.DEBUG)

    # Log to stderr.
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Create a thread to run the web server.
    t = threading.Thread(
        target=app.run,
        kwargs={ 'host' : '127.0.0.1',
                 'port' : 5000,
                 'use_reloader' : False,
                 'threaded' : 4 })
    t.daemon = True
    t.start()

    # Register the module to be livecoded.
    app.window.set_module(module_path)
    
    # Run the PyLive window main loop.
    app.window.run()

def main():
    from optparse import OptionParser, OptionGroup
    parser = OptionParser("""%prog [options] <module path>""")
    opts,args = parser.parse_args()

    if len(args) != 1:
        parser.error("invalid number of arguments")

    module_path, = args

    # Create the application.
    run_pylive(module_path)

if __name__ == '__main__':
    main()
