import argparse


class Parser:

    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.initialize_arguments()
        self.parse_arguments()

    def initialize_arguments(self):

        self.parser.add_argument("--test",               # Only launch tests
                                 action="store_true",    # Syntactic sugar to say 'default:"false"'
                                 help="Do not launch the server, only launch tests")
        self.parser.add_argument("--debug", "-d",        # Enable Debug Logging
                                 action="store_true",    # Copied from above
                                 help="Verbose/Debug logging")

    def parse_arguments(self):
        self.args = self.parser.parse_args()
        self.test = self.args.test
        self.debug = self.args.debug
