import argparse


class Parser:

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.initialize_arguments()
        self.parse_arguments()

    def initialize_arguments(self):
        self.parser.add_argument("--debug",              # Command line flag to set logging in DEBUG mode
                                 action="store_true",    # Syntactic sugar to say 'default:"false"'
                                 help="Set logging to DEBUG level")
        self.parser.add_argument("--test",               # Only launch tests
                                 action="store_true",    # Syntactic sugar to say 'default:"false"'
                                 help="Do not launch the server, only launch tests")
        self.parser.add_argument("--format",             # Command line flag to set the log format
                                 nargs='?',              # We expect another argument after that
                                 default="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s",
                                 help="Set the logging format to the specified format. (Default: \"%(default)s\")")

    def parse_arguments(self):
        self.args = self.parser.parse_args()
        self.debug = self.args.debug
        self.test = self.args.test
        self.format = self.args.format
