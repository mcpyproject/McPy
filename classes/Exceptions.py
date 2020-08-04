# coding=utf-8
# Basic exceptions for mcPy


class MinecraftException(Exception):
    pass


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
