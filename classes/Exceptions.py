# coding=utf-8
# Basic exceptions for mcPy


class MinecraftException(Exception):
    def __init__(self, e=None):
        self.exception = e


class ServerException(MinecraftException):
    pass


class WorldError(ServerException):
    pass


class SaveError(WorldError):
    pass


class NoiseGeneratorException(WorldError):
    pass


class ChunkError(WorldError):
    pass


class OutOfBoundsError(ChunkError):
    pass


class ChunkNotFound(ChunkError):
    pass


class ChunkExistsError(ChunkError):
    pass


class ClientException(MinecraftException):
    pass


class ConfigParserException(Exception):
    def __init__(self, e=None):
        self.exception = e


class NotAFileError(ConfigParserException):
    pass


class UnsupportedConfigType(ConfigParserException):
    pass


class FormattingError(ConfigParserException):
    pass
