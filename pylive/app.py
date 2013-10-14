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
        self.window = window.Window('PyLive', 400, 400)

###
# Server Entrypoint

def main():
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

    # Run the PyLive window main loop.
    app.window.run()

if __name__ == '__main__':
    main()
