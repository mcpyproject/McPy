import logging
import multiprocessing
import os
import sys
import psutil

from .Parser import Parser
import classes.Server as Server
from classes.utils.Config import ConfigParser

config = ConfigParser.load_config(1)


def get_available_core():
    avail_cores = psutil.cpu_count()
    return avail_cores


def _launch(parser: Parser):
    if (config['use_blackfire'] == True):
        try:
            from blackfire import probe
            probe.initialize()
            probe.enable()
            logging.info("Blackfire Enabled!")
            BLACKFIRE_ENABLED = True
        except ModuleNotFoundError:
            logging.info("Blackfire Module not found; passing!")
            BLACKFIRE_ENABLED = False
    else:
        BLACKFIRE_ENABLED = False


    logging.info("Loading data files, please wait ...")
    # TODO Import it in another class
    logging.info("Data files loaded !")
    logging.info("Importing Minecraft data, please wait ...")
    from classes.blocks.Materials import Material
    from classes.utils.DataParser import DataParser
    from classes.utils.Utils import Version
    versions_string = [ # Theoretically, other versions could be added here
        '1.15.2'
    ]
    dataparser = DataParser(versions=versions_string)
    data, versions = dataparser.parse()
    Material.load_all_data(versions, data)

    avail_cores = get_available_core()

    # Here starts the server :D
    server = Server.Server(parser, avail_cores)
    if parser.test:
        server.run_test()
        return
    server.start(config['ip'], config['port'])

    # End Network stuff
    server.stop()
    if BLACKFIRE_ENABLED:
        probe.end()
    logging.info("Server stopped: goodbye!")
    sys.exit(0)


def main():
    parser = Parser()

    if parser.debug:
        logging.info('Debug mode enabled. Don\'t forget to remove debug flag for maximum performance !')
    logging_level = logging.DEBUG if parser.debug else logging.INFO
    logging.basicConfig(level=logging_level, format=parser.format, force=True)

    _launch(parser)
