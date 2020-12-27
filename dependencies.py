import logging
import sys
import subprocess
import json

# Set default logging level to INFO
logging.basicConfig(level="INFO")

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal('McPy needs Python version 3.8.0 or higher to run! Current version is %s.%s.%s' % (
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    sys.exit(-4)

# Make sure pip is installed
logging.info("Making sure pip is installed...")
subprocess.check_call([sys.executable, '-m', 'ensurepip'])
logging.info("Pip is installed")

# Make sure that dependencies are installed
logging.info("Checking for dependencies...")
try:
    import quarry
except ImportError:
    logging.info("Quarry not installed! Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'quarry'])
try:
    import pytest
except ImportError:
    logging.info("PyTest not installed! Installing...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytest'])
subprocess.check_call(['git', 'init'])
subprocess.check_call(['git', 'submodule', 'init'])
subprocess.check_call(['git', 'submodule', 'update'])
logging.info("Dependencies installed")

# Finishing up
with open('releases.json', 'r') as f:
    release_info = json.load(f)

for releases in release_info:
    version = releases["mcpyVersion"]

logging.info("McPy version " + version + " is ready.")
# Starts McPy
try:
    subprocess.check_call([sys.executable, 'main.py'])
    logging.info("McPy started!")
except KeyboardInterrupt: # Catches keyboard interrupt caused by Crt-Cing the server process due to it being a subprocess
    logging.info("McPy stopped! Run main.py next time to start the server!")