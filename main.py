# coding=utf-8
import logging
import sys

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal(
        'McPy needs Python version 3.8.0 or higher to run! Current version is %s.%s.%s',
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro)
    sys.exit(-2)

import classes

logging.basicConfig(level=logging.INFO, format='[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s', force=True)

if __name__ == "__main__":
    classes.mcPy.main()
