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

def run_pylive(host, port, module_path):
    app = App(__name__)
    app.debug = True

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
        kwargs={ 'host' : host,
                 'port' : port,
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
    parser.add_option("", "--hostname", dest="hostname", type=str,
                      help="host interface to use [%default]",
                      default='127.0.0.1')
    parser.add_option("", "--port", dest="port", type=int, metavar="N",
                      help="local port to use [%default]", default=5000)
    opts,args = parser.parse_args()

    if len(args) != 1:
        parser.error("invalid number of arguments")

    module_path, = args

    # Create the application.
    run_pylive(opts.hostname, opts.port, module_path)

if __name__ == '__main__':
    main()
