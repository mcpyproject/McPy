# coding=utf-8
# Version release dict key requirements
# "mcpyVersion" = McPy version number
# "minecraftVersion" = Minecraft version number
# "releaseDate" = this version's release date
# "downloadLink" = URL to the download of this server archive
# "md5sum" = MD5 sum of the download
# "sha1sum" = SHA1 sum of the download
import os
import sys
import logging
import json
import requests
import subprocess
import zipfile
import hashlib
import argparse
import pkg_resources


parser = argparse.ArgumentParser()
parser.add_argument("--useversion",    # Command line flag to use McPy version
                    action="store",    # Stores result of this flag in parsedArgs.useversion
                    default="latest",  # Defaults to "latest" if this flag is not passed
                    help="version to use: defaults to latest")
parser.add_argument("--versions",         # Command line flag to print out list of all versions
                    action="store_true",  # If this flag is defined, parsedArgs.versions will be True: else False
                    help="print out a list of all McPy versions")
parser.add_argument("--pythonlocation",  # Command line flag to define a Python interpeter location
                    action="store",      # Stores the result of this flag in parsedArgs.pythonlocation
                    default=None,        # If not passed, defaults to None
                    help="location of the Python 3.8 interpeter: defaults to the one found in the path")
parsedArgs = parser.parse_args()


# Automagically installs all packages required
required = {"quarry", "twisted", "cryptography"}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed
if missing:
    # implement pip as a subprocess:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing])


def getReleases() -> list:
    global releases
    try:
        if releases is not None:
            logging.info("Using cached release list!")
            return releases
    except NameError:
        pass  # Some people want to kill me for this but there's a meaning behind it
    logging.info("Getting release list...")
    releaseFile = requests.get("https://raw.githubusercontent.com/tazz4843/McPy/master/releases.json")  # All releases
    try:
        releaseFile.raise_for_status()
    except requests.exceptions.RequestException as ex:
        logging.fatal("Failed to get update file! Try running this script again. Error: {0}".format(str(ex)))
        sys.exit(-1)
    releases = json.loads(releaseFile.text)
    if len(releases) == 0:
        logging.fatal("No McPy releases have been created yet! Check back again shortly.")
        sys.exit(-2)
    return releases


def checkSums(fileName, bufferSize=64*1024):
    """
    Quick utility to check the hashes of a file
    :param fileName: Name of the file to hash
    :param bufferSize: Defaults to 64*1024: amount of bytes to read each chunk
    :return: List of sums: md5 is 1st, sha1 is 2nd
    """
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()

    with open(fileName, 'rb') as f:
        while True:
            data = f.read(bufferSize)
            if not data:
                break
            md5.update(data)
            sha1.update(data)
    return [md5.hexdigest(), sha1.hexdigest()]


releases = getReleases()

systemPath = ":".join(sys.path)
if "python3.8" not in systemPath:
    if parsedArgs.pythonlocation is None:
        logging.fatal("Python 3.8 was not found in the system path! You can specify the Python 3.8 executable location"
                      "using --pythonlocation <pathToExecutable>")
        sys.exit(-4)
    else:
        PYTHONINPATH = False
else:
    PYTHONINPATH = True

if parsedArgs.versions:
    for item in releases:
        print("Release version {0} released on {1} for Minecraft version {2}".format(item["mcpyVersion"],
                                                                                     item["releaseDate"],
                                                                                     item["minecraftVersion"]))
    print("For latest version, pass \"latest\" to the --useversion flag, or don't pass the --useversion flag at all.")
    sys.exit(-3)

version = parsedArgs.useversion
pythonlocation = parsedArgs.pythonlocation

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
    logging.info("Unzipping files...")
    with open("mcPyTempFile.zip", "wb") as zf:
        for j in downloadedServer.iter_content(100000):  # 100,000 bytes each time to be safe
            zf.write(j)
    logging.info("Checking checksums...")
    sums = checkSums("mcPyTempFile.zip")
    if sums[0] != version["md5sum"] or sums[1] != version["sha1sum"]:
        logging.fatal("MD5 or SHA-1 sum does NOT MATCH! This could be a corruption, or it could be something more "
                      "serious, like someone tampering with your connection.")
        sys.exit(-10)
    with zipfile.ZipFile("mcPyTempFile.zip") as mcpyZipFile:
        mcpyZipFile.extractall()
    logging.info("To run McPy, rerun this script!")
else:
    logging.info("McPy found! Running it...")
    if PYTHONINPATH:
        mcpyProcess = subprocess.Popen("python3.8 McPy/main.py")
    else:
        mcpyProcess = subprocess.Popen("{0} McPy/main.py".format(pythonlocation))
    mcpyProcess.wait()
