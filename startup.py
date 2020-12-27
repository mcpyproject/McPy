# coding=utf-8
# Version release dict key requirements
# "mcpyVersion" = McPy version number
# "minecraftVersion" = Minecraft version number
# "releaseDate" = this version's release date
# "downloadLink" = URL to the download of this server archive
# "md5sum" = MD5 sum of the download
# "sha1sum" = SHA1 sum of the download
import argparse
import ensurepip
import hashlib
import json
import logging
import os
import subprocess
import sys
import zipfile

import pkg_resources


# Set default logging level to INFO
logging.basicConfig(level="INFO")

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal('McPy needs Python version 3.8.0 or higher to run! Current version is %s.%s.%s' % (
        sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    sys.exit(-4)

logging.info("Making sure pip is installed...")
ensurepip.bootstrap(upgrade=True)
logging.info("Installed.")

try:
    import requests
except ImportError:
    logging.fatal("requests is not installed! Installing right now...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    logging.info("Installed! Rerun this script.")
    sys.exit(1)

parser = argparse.ArgumentParser()
parser.add_argument("--useversion",    # Command line flag to use McPy version
                    action="store",    # Stores result of this flag in parsedArgs.useversion
                    default="latest",  # Defaults to "latest" if this flag is not passed
                    help="version to use: defaults to latest")
parser.add_argument("--versions",         # Command line flag to print out list of all versions
                    action="store_true",  # If this flag is defined, parsedArgs.versions will be True: else False
                    help="print out a list of all McPy versions")
parser.add_argument("--launcher",        # options to pass to main.py
		   action="store",
		   default="none",
		   help="options to pass to main.py (main server)")
parser.add_argument("--ignoreCheck",     # ignore file check and download check if passed          
		   action="store",
		   default="False",
		   help="Ignore MD5 check and download check")
parsedArgs = parser.parse_args()


# Automagically installs all packages required
required = {"quarry", "twisted", "cryptography", "requests", "pytest"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    # implement pip as a subprocess:
    # This prevents SyntaxError while launching with python2: use this instead of *missing
    data = [sys.executable, '-m', 'pip', 'install'] + [miss for miss in missing]
    subprocess.check_call(data)


def get_releases() -> list:
    """
    Gets latest release list
    :return: list of releases
    """
    global releases
    try:
        if releases is not None:
            logging.info("Using cached release list!")
            return releases
    except NameError:
        pass  # Some people want to kill me for this but there's a meaning behind it
    logging.info("Getting release list...")
    release_file = requests.get("https://raw.githubusercontent.com/tazz4843/McPy/master/releases.json")  # All releases
    try:
        release_file.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logging.fatal("Failed to get update file! Try running this script again. Error: {0}".format(str(ex)))
        sys.exit(-1)
    releases = json.loads(release_file.text)
    if len(releases) == 0:
        logging.fatal("No McPy releases have been created yet! Check back again shortly.")
        sys.exit(-2)
    return releases


def check_sums(file_name, buffer_size: int = 65536):
    """
    Quick utility to check the hashes of a file
    :param file_name: Name of the file to hash
    :param buffer_size: Defaults to 65,536: amount of bytes to read each chunk
    :return: List of sums: md5 is 1st, sha1 is 2nd
    """
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(file_name, 'rb') as f:
        while True:
            _data = f.read(buffer_size)
            if not _data:
                break
            md5.update(_data)
            sha1.update(_data)
    return [md5.hexdigest(), sha1.hexdigest()]


releases = get_releases()

if parsedArgs.versions:
    for item in releases:
        print("Release version {0} released on {1} for Minecraft version {2}".format(item["mcpyVersion"],
                                                                                     item["releaseDate"],
                                                                                     item["minecraftVersion"]))
    print("For latest version, pass \"latest\" to the --useversion flag, or don't pass the --useversion flag at all.")
    sys.exit(-3)

version = parsedArgs.useversion

launcherArgs = parsedArgs.launcher
		
version = parsedArgs.useversion
ignoreCheck = parsedArgs.ignoreCheck
if ignoreCheck == True:
	print("Ignoring File System and Download Check")
	import classes
	if __name__ == "__main__":
		classes.mcPy.main(launcherArgs)

else:
	currentDir = os.listdir(".")
	if "McPy" not in currentDir:
		logging.warning("main.py not found! Downloading McPy again...")
		if version == "latest":
			logging.info("Downloading latest version...")
			version = releases[len(releases) - 1]
			downloadLink = version["downloadLink"]
		else:
			downloadLink = None
			for v in releases:
				if v["mcpyVersion"] == version:
					version = v
					downloadLink = v["downloadLink"]
					break
			if downloadLink is None:
				logging.fatal("No download link found!")
		logging.info("Downloading McPy server files...")
		downloadedServer = requests.get(downloadLink)
		try:
			downloadedServer.raise_for_status()
		except requests.exceptions.RequestException as e:
			logging.error("Failed to download the server file! Rerun this script. Error: {0}".format(str(e)))
		else:
			logging.info("Successfully downloaded McPy!")
		logging.info("Writing zip file...")
		with open("mcPyTempFile.zip", "wb") as zf:
			for j in downloadedServer.iter_content(100000):  # 100,000 bytes each time to be safe
				zf.write(j)
		logging.info("Checking checksums...")
		sums = check_sums("mcPyTempFile.zip")
		if sums[0] != version["md5sum"] or sums[1] != version["sha1sum"]:
			logging.fatal("MD5 or SHA-1 sum does NOT MATCH! This could be a corruption, or it could be something more "
						"serious, like someone tampering with your connection.")
			sys.exit(-10)
		logging.info("Extracting file...")
		with zipfile.ZipFile("mcPyTempFile.zip") as mcpyZipFile:
			mcpyZipFile.extractall()
		# Delete temp file mcPyTempFile.zip
		logging.info("Cleaning up...")
		os.remove("mcPyTempFile.zip")
		logging.info("To run McPy, rerun this script!")
		sys.exit(1)
	else:
		logging.info("McPy found! Running it...")
		import classes
		if __name__ == "__main__":
			classes.mcPy.main(launcherArgs)
