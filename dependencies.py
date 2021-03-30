import logging
import sys
import subprocess
import json

# Set default logging level to INFO
logging.basicConfig(level="INFO", format="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s", force=True)

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal('McPy needs Python version 3.8.0 or higher to run! Current version is %s.%s.%s' % (
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    sys.exit(-4)

# Make sure pip is installed
logging.info("Making sure pip is installed...")
try: # Debian and Ubuntu require pip to be installed differently because they disable ensurepip
    import distro
    linuxDistro = distro.linux_distribution()
    if linuxDistro[0] == "Debian" or linuxDistro[0] == "Ubuntu":
        try:
            subprocess.check_call(['apt', 'install', 'python3-pip', '-y'])
        except subprocess.CalledProcessError:
            logging.fatal("You need to be the superuser to install pip and the dependencies")
            sys.exit(-4)
except ModuleNotFoundError: # If the system is not Linux, the module "distro" will not load, causing a ModuleNotFoundError exception and the normal "ensurepip" module will work
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
except subprocess.CalledProcessError as e:
    if (e.returncode == 127):
        logging.fatal("Git is not installed! Please install it!")
except FileNotFoundError:
    logging.fatal("Git is not installed! Please install it!")
    sys.exit(-1)

# Finishing up
with open('releases.json', 'r') as f:
    release_info = json.load(f)

for releases in release_info:
    version = releases["mcpyVersion"]

logging.info("McPy version " + version + " is ready. You can run the server with python3 main.py")
