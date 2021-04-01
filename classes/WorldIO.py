""" API Class for accessing things in the World """
from .BasicClasses import Block, Chunk, Region
from .blocks.Materials import Material


class BasicBlockContainer:
    """ BasicBlockContainers are used to cache changes of Blocks in a Chunk, reducing the amount of required WorldIO.
     Please note that this class is mostly meant to cache additions, and as such will have memory leaks when updating
     a block multiple times as well being only sorted in insertion order """
    def __init__(self):
        self.container: [(int, int, int, Block)] = []

    def addBlock(self, blockX: int, blockY: int, blockZ: int, block: Block):
        """ Adds a block to the container; blockX, blockY and blockZ are relative to the container origin, what it means
        is left to the whatever function that formalises the changes. """
        self.container.append((blockX, blockY, blockZ, block))


def mergeContainers(destination: BasicBlockContainer,
                    source: BasicBlockContainer,
                    offsetX: int = 0,
                    offsetY: int = 0,
                    offsetZ: int = 0):
    """ Merges the specified source container into the specified destination container with a configurable offset.
    The source container will be handled last in the formalisation process"""
    for item in source.container:
        destination.container.append((item[0]+offsetX, item[1]+offsetY, item[2]+offsetZ, item[3]))


def getChunk(chunkX: int, chunkY: int, chunkZ: int) -> Chunk:
    """ Returns the Chunk  at a given position relative to origin in chunk sizes. A chunk is 16 blocks wide.
      It may raise a ChunkNotFound exception if the requested chunk does not exist."""
    pass


def getRegion(regionX: int, regionY: int, regionZ: int) -> Region:
    """ Returns the Region at a given position relative to origin in region sizes.
    A region is 32 chunks large which are 512 blocks in total. """
    pass


def getBlockAt(blockX: int, blockY: int, blockZ: int) -> Block:
    """ Returns the Block at a given position relative to origin """
    pass


def setMaterialAt(blockX: int, blockY: int, blockZ: int, newMaterial: Material):
    """ Sets the Material of a block at a given position relative to origin to the given Material. """
    pass


def formaliseChunk(chunkX: int, chunkY: int, chunkZ: int, changes: BasicBlockContainer):
    """ Applies changes stated in the given BasicBlockContainer to a chunk with a given position relative to origin
     in Chunk sizes. It may raise a ChunkNotFound exception if the chunk does not exist. """
    pass
