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

    def parse_arguments(self):
        self.args = self.parser.parse_args()
        self.debug = self.args.debug
        self.test = self.args.test