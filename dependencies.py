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

# If the OS is Linux, the module "distro" will import
try:
    import distro
except ModuleNotFoundError: # Windows and MacOS will not find this module, because they don't have distributions
    pass

# Make sure pip is installed
logging.info("Making sure pip is installed...")
try: # Debian and Ubuntu require pip to be installed differently because they disable ensurepip
    linuxDistro = distro.linux_distribution()
    if linuxDistro[0] == "Debian":
        subprocess.check_call(['sudo', 'apt', 'install', 'python3-pip'])
    if linuxDistro[0] == "Ubuntu":
        subprocess.check_call(['sudo', 'apt', 'install', 'python3-pip'])
except NameError: # If the system is not Linux, the module "distro" will not load, causing a NameError exception and the normal "ensurepip" module will work
    subprocess.check_call([sys.executable, '-m', 'ensurepip']) # The module ensure pip check if pip is installed and installs it if it isn't
logging.info("Pip is installed")

# Make sure that dependencies are installed
logging.info("Installing dependencies...")
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
try:
    subprocess.check_call(['git', 'init'])
    subprocess.check_call(['git', 'submodule', 'init'])
    subprocess.check_call(['git', 'submodule', 'update'])
    logging.info("Dependencies installed")
except subprocess.CalledProcessError:
    logging.fatal("Git is not installed! Please install it!")

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
except KeyboardInterrupt: # Catches keyboard interrupt caused by Ctrl-Cing the server process due to it being a subprocess
    logging.info("McPy stopped! Run main.py next time to start the server!")