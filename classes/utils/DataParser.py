import json
import logging
import re
import os
import time

from enum import Enum
from .Utils import Version


class DataParser():
    """
    A class that is used to parse, retrieve and store in memory data taken from https://github.com/PrismarineJS/minecraft-data.
    This class will retrieves data for given minecraft versions. If no version is provided, 

    Methods
    -------
    Parser(file, submodule='', namespace_id='namespace_id', struct={}, id_path='')
        Register a class that will be parsed later

    parse_enums()
        Load classes that have been registered previously.
        You can call this method multiple times, classes already loaded will not be reloaded
    """

    def __init__(self, directory='minecraft-data/', versions=['all']):
        """
        Register a class in the parser to load and import data from a json file.

        This method does NOT parse the file!
        Please call Parser.parse_enums() to load datas

        Parameters
        ----------
        directory : str
            The name of the directory where repository is.
            Default = 'minecraft-data/'

        versions : array
            A list of versions to import. Add 'all' to import all versions
        """
        if len(directory) > 0 and directory[-1] != '/':
            directory = directory + '/'
        self.root_directory = directory
        self.data_directory = directory + 'data/'
        if 'all' in versions:
            # Import all versions
            self.versions = [v for v in Version]
        else:
            self.versions = list(filter(None.__ne__, [Version.get_version_data_file(v) for v in versions]))

    def parse(self):
        with open(self.data_directory + 'dataPaths.json') as json_file:
            data_paths = json.load(json_file)
        result = {}
        versions = []
        for version in self.versions:
            if version.data_id not in data_paths['pc']:
                logging.error('Cannot import version %s because it hasn\'t be found in dataPaths.json file', version)
                continue
            versions.append(version)
            result[version.data_id] = {}
            version_data_paths = data_paths['pc'][version.data_id]
            # Import blocks
            result[version.data_id]['blocks'] = self._read_property(version_data_paths, 'blocks')
            result[version.data_id]['blockCollisionShapes'] = self._read_property(version_data_paths, 'blockCollisionShapes')
            result[version.data_id]['biomes'] = self._read_property(version_data_paths, 'biomes')
            result[version.data_id]['enchantments'] = self._read_property(version_data_paths, 'enchantments')
            result[version.data_id]['effects'] = self._read_property(version_data_paths, 'effects')
            result[version.data_id]['items'] = self._read_property(version_data_paths, 'items')
            result[version.data_id]['recipes'] = self._read_property(version_data_paths, 'recipes')
            result[version.data_id]['instruments'] = self._read_property(version_data_paths, 'instruments')
            result[version.data_id]['materials'] = self._read_property(version_data_paths, 'materials')
            result[version.data_id]['entities'] = self._read_property(version_data_paths, 'entities')
            result[version.data_id]['protocol'] = self._read_property(version_data_paths, 'protocol')
            result[version.data_id]['windows'] = self._read_property(version_data_paths, 'windows')
            result[version.data_id]['version'] = self._read_property(version_data_paths, 'version')
            result[version.data_id]['language'] = self._read_property(version_data_paths, 'language')
            result[version.data_id]['foods'] = self._read_property(version_data_paths, 'foods')
            result[version.data_id]['particles'] = self._read_property(version_data_paths, 'particles')
            result[version.data_id]['blockLoot'] = self._read_property(version_data_paths, 'blockLoot')
            result[version.data_id]['entityLoot'] = self._read_property(version_data_paths, 'entityLoot')
            result[version.data_id]['loginPacket'] = self._read_property(version_data_paths, 'loginPacket')
        return result, versions

    def _read_property(self, version_data_paths, property):
        if property in version_data_paths:
            directory_version_blocks = version_data_paths[property]
            with open(self.data_directory + directory_version_blocks + '/{}.json'.format(property)) as json_file:
                return json.load(json_file)
        return None
