import logging
import multiprocessing
import os
import sys

from .Parser import Parser
import classes.Server as Server


def get_available_core():
    try:
        avail_cores = len(os.sched_getaffinity(0))
    except AttributeError:
        # Fix for windows, which doesnt support getaffinity
        logging.warning(
            "Falling back to multiprocessing cpu_count to calc cores. Most likely getaffinity is not supported on "
            "your OS")
        avail_cores = multiprocessing.cpu_count()
    return avail_cores


def _launch(parser: Parser):
    try:
        # noinspection PyUnresolvedReferences
        from blackfire import probe  # Profiler: https://blackfire.io free with the Git Student Package
    except ImportError:
        BLACKFIRE_ENABLED = False
        logging.info("Blackfire not installed: passing")
    else:
        BLACKFIRE_ENABLED = True
        probe.initialize()
        probe.enable()
        logging.info("Blackfire Enabled!")

    avail_cores = get_available_core()

    # Here starts the server :D
    server = Server.Server(parser, avail_cores)
    if parser.test:
        server.run_test()
        return
    server.start()

    # End Network stuff
    server.stop()
    if BLACKFIRE_ENABLED:
        probe.end()
    logging.info("Server stopped: goodbye!")
    sys.exit(0)


def main():
    parser = Parser()

    if parser.debug:
        print('Debug mode enabled. Don\'t forget to remove debug flag for maximum performance !')
    logging_level = logging.DEBUG if parser.debug else logging.INFO
    logging.basicConfig(level=logging_level, format=parser.format, force=True)

    _launch(parser)
