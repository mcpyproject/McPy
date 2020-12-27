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


def _launch(args):
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
    if "coreCount" in args:
	logging.warning("Core Count flag set, only use this if you know what your doing. If you get an error turn off core count first")
	for item in args:
		if Item == "coreCount":
			splitItem = item.split("=")
			avail_cores = splitItem[1]
    else:
    	avail_cores = get_available_core()

    # Here starts the server :D
    server = Server.Server(args, avail_cores)
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


def main(args):
    parsedArgs = args.split(",")
    if "debug=true" in parsedArgs:
        print('Debug mode enabled. This may slow down your server on slower hardware but not on newer hardware')
    logging_level = logging.DEBUG if "debug=true" in parsedArgs else logging.INFO
    logging.basicConfig(format="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s")
    logging.root.setLevel(logging_level)
    

    _launch(parsedArgs)
