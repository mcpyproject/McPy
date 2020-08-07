# coding=utf-8
import os
import sys
import logging
import json
import requests
import subprocess
import zipfile
import hashlib


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
    except requests.exceptions.RequestException:
        logging.fatal("Failed to get update file! Try running this script again.")
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
    logging.fatal("Python 3.8 was not found in the system path! You can specify the Python 3.8 executable location"
                  "using --pythonlocation <pathToExecutable>")
    sys.exit(-4)
else:
    PYTHONINPATH = True

if "--versions" in sys.argv:
    for item in releases:
        print("Release version {0} released on {1} for Minecraft version {2}".format(item["mcpyVersion"],
                                                                                     item["releaseDate"],
                                                                                     item["minecraftVersion"]))
    print("For latest version, pass \"latest\" as the version.")
    sys.exit(-3)
elif "--help" in sys.argv:
    print("McPy command line flags:")
    print("--versions               List all available versions.")
    print("--useversion <version>   Select version <version>.")
    print("\n")
elif "--useversion" in sys.argv:
    version = None
    for item, i in zip(sys.argv, range(len(sys.argv))):
        if item == "--useversion":
            try:
                version = sys.argv[i + 1]  # Gets next element in sys.argv, which should be the argument to --useversion
            except KeyError:
                logging.fatal("No version specified!")
                sys.exit(-3)
            break
    if version is None:
        logging.fatal("No version specified!")
        sys.exit(-3)
elif "--pythonlocation" in sys.argv:
    pythonLocation = None
    for item, i in zip(sys.argv, range(len(sys.argv))):
        if item == "--pythonlocation":
            try:
                pythonLocation = sys.argv[i + 1]  # Gets next element in sys.argv, which should be the argument to
                # --useversion
            except KeyError:
                logging.fatal("No Python location specified!")
                sys.exit(-4)
            break
    if pythonLocation is None:
        logging.fatal("No Python location specified!")
        sys.exit(-3)
elif "--useversion" not in sys.argv:
    logging.fatal("No version specified!")
    logging.info("Specify a version using --useversion")
    logging.info("List versions using --versions")
    logging.info("Use latest version with --useversion latest")
    sys.exit(-5)

currentDir = os.listdir(".")
if "main.py" not in currentDir:
    logging.warning("main.py not found! Downloading McPy again...")
    # noinspection PyUnboundLocalVariable
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
    with open("mcPyTempFile.zip", "w") as zf:
        for j in downloadedServer.iter_content(100000):  # 100,000 bytes each time to be safe
            zf.write(j)
    logging.info("Checking checksums...")
    sums = checkSums("mcPyTempFile.zip")
    # noinspection PyTypeChecker
    if sums[0] != version["sha1sum"] or sums[1] != version["sha1sum"]:
        logging.fatal("MD5 or SHA-1 sum does NOT MATCH! This could be a corruption, or it could be something more "
                      "serious, like someone tampering with your connection.")
        sys.exit(-10)
    with zipfile.ZipFile("mcPyTempFile.zip") as mcpyZipFile:  # Because Python's special and can't just pipe it
        # straight in
        mcpyZipFile.extractall()
    logging.info("To run McPy, rerun this script!")
else:
    logging.info("McPy found! Running it...")
    if PYTHONINPATH:
        mcpyProcess = subprocess.Popen("python3.8 main.py")
    else:
        # noinspection PyUnresolvedReferences
        if os.isfile(pythonLocation):
            mcpyProcess = subprocess.Popen("{0} main.py".format(pythonLocation))
        else:
            logging.fatal("Python location is not a file! Check you've passed the right path!")
            sys.exit(-5)
    # noinspection PyUnresolvedReferences
    mcpyProcess.join()
