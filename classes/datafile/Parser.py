import json
import re
import os
import time

from enum import Enum


class Parser():
    """
    A class that is used to parse, retrieve and store in memory a json file.

    This is mainly used to import minecraft generated data but this could also be used to import other kind of json file.

    Attributes
    ----------
    directory : str\n
        \tDirectory where are datas. This is unique for all the application

    Methods
    -------
    Parser(file, submodule='', namespace_id='namespace_id', struct={}, id_path='')\n
        \tRegister a class that will be parsed later

    parse_enums()\n
        \tLoad classes that have been registered previously.\n
        You can call this method multiple times, classes already loaded will not be reloaded
    """

    to_parse = []
    parsed = []
    # Pre-Compile it to gain speed
    slash_pattern = re.compile(r"\/", re.IGNORECASE)

    def __init__(self):
        pass

    @staticmethod
    def Parser(file, directory='cache/generated/{version}/', namespace_id='namespace_id', struct={}, array_path='', key_pattern='{key}'):
        """
        Register a class in the parser to load and import data from a json file.

        This method does NOT parse the file!
        Please call Parser.parse_enums() to load datas

        Parameters
        ----------
        file : str\n
            \tThe path from the version directory to the file

        directory : str\n
            \tThe name of the directory where versions are.
            \tDefault = 'cache/generated/{version}/'

        namespace_id : str\n
            \tThe name of the variable where is store the id of the namespace. Default to `namespace_id`

        struct : dict\n
            \tThe structure of the json file

        array_path : str\n
            \tA string representing the path in json file between the root and arrays containing each element.
            \tThe parser will directly goes to this point. That means that any elements that are parent to this path will not be saved neither parsed again

        key_pattern : str\n
            \tThe pattern to use to match keys used in enumeration and keys used in file.
            \tDefault = '{key}'
        """
        def int_func(cls):
            if not issubclass(cls, Enum):
                raise ValueError('Class %s does not extends class Enum !' % (cls.__name__))
            directory_version_split = re.split(r"{version}", directory, flags=re.IGNORECASE)
            versions = Parser._retrieve_versions(directory_version_split[0])
            suffix = directory_version_split[1] if len(directory_version_split) > 1 and directory_version_split[1] else '/'
            if suffix[-1] != '/':
                suffix = suffix + '/'

            datas = {
                "_file": file,
                "_directory": directory,
                "_dirs": {
                    "prefix": directory_version_split[0],
                    "suffix": suffix,
                },
                "_namespace_id": namespace_id,
                "_struct": struct,
                "_array_path": array_path,
                "_versions": versions,
                "_key_pattern": key_pattern,
                "_cls": cls,
            }

            Parser.to_parse.append(datas)
            cls._datas = datas
            return cls
        return int_func

    @staticmethod
    def parse_enums():
        for to_parse in Parser.to_parse:
            before_time = int(time.time() * 1000)
            print('Loading file %s' % (to_parse['_file']))
            # Retrieves namespace id in enum
            namespace_ids = Parser._retrieve_namespace_id(to_parse['_cls'], to_parse['_namespace_id'])

            # Set empty protocol
            for n_id in namespace_ids:
                namespace_ids[n_id].protocol = {}

            for version in to_parse['_versions']:
                full_path_file = '%s%s%s%s' % (to_parse['_dirs']['prefix'], version, to_parse['_dirs']['suffix'], to_parse['_file'])
                Parser._import_json(full_path_file, to_parse, version, namespace_ids)

            after_time = int(time.time() * 1000)
            print('File loading in %d ms' % (after_time - before_time))
        # Clear to_parse to avoid reimporting imported values
        Parser.to_parse = []

    @staticmethod
    def _retrieve_versions(directory) -> dict:
        """
        Retrieves directories names that are at a specific location

        This is used to retrieve version names

        Parameters
        ----------
        directory : str\n
            \tThe directory where are versions
        """
        return [f.name for f in os.scandir(directory) if f.is_dir()]

    @staticmethod
    def _retrieve_namespace_id(cls, namespace_id):
        """
        Retrieve namespace ids and make a link between the id and the enum

        Parameters
        ----------
        cls : Enum\n
            \tEnum class where we'll retrieve namespace ids

        namespace_id : str\n
            \tThe name of the variable where are stored namespace id
        """
        return {getattr(elem, namespace_id): elem for elem in cls}

    @staticmethod
    def _import_json(file, obj, version, namespace_ids):
        """
        Read, import and load a single json file

        This method knows the structure of the json file

        Parameters
        ----------
        file : str\n
            \tThe name of the file to import
        obj : type\n
            \tData of the object containing the structure of json file and the original class
        version : str\n
            \tThe version of this file
        namespace_ids : dict\n
            \tDictionary containing as key the namespace id and as value the enum associated with this id
        """
        struct = obj['_struct']
        array_path = obj['_array_path']
        key_pattern = obj['_key_pattern']
        cls = obj['_cls']

        try:
            with open(file) as json_file:
                data = json.load(json_file)
                # Go in depth until we're at array_path
                for p in Parser.slash_pattern.split(array_path):
                    if p:
                        data = data[p]
                # Once we're where array_path want to be, we'll loop over each element in our enum
                for id in namespace_ids:
                    id_key = key_pattern.replace('{key}', id)
                    # Check if it exists in the json file. If not, no need to parse it (because it doesn't exist)
                    enum_cls = namespace_ids[id]
                    if id_key not in data:
                        continue
                    # It exists, let's make the structure
                    result = {}
                    enum_cls.protocol[version] = result
                    Parser._parse_struct(struct, data[id_key], cls, result, enum_cls)
        except FileNotFoundError:
            print('File %s doesn\'t exist !' % (file))

    @staticmethod
    def _parse_struct(struct, elem, cls, result, enum_cls):
        for s in struct:
            if s == '_action':
                # Action to execute
                actions = struct[s]
                if not isinstance(actions, list):
                    actions = [actions]
                for action in actions:
                    if action['type'] == 'call_method':
                        # Call this method
                        getattr(cls, action['method'])(enum_cls, result, elem)
                    elif action['type'] == 'save':
                        result[action['id']] = elem
            else:
                # if not isinstance(elem, dict):
                #     continue
                sub_elem = elem[s] if s in elem else None
                if sub_elem is not None:
                    Parser._parse_struct(struct[s], sub_elem, cls, result, enum_cls)
