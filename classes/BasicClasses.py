# coding=utf-8

from classes import Exceptions
import asyncio


class Block:
    def __init__(self, x: int, y: int, z: int, _id: str, data: [dict, None]):
        self.xPos = x
        self.yPos = y
        self.zPos = z
        self.id = _id
        self.blockData = data


class BlockEntity(Block):
    def __init__(self, x, y, z, _id, data: [dict, None], blockEntityData):
        super().__init__(x, y, z, _id, data)
        self.blockEntityData = blockEntityData


class Region:
    def __init__(self, RegionXPos, RegionYPos, subChunks: dict):
        self.location = (RegionXPos, RegionYPos)
        self.subChunkList = subChunks

    def getChunk(self, x, y):
        return self.subChunkList["{0},{1}".format(x, y)].getChunk()


class Chunk:
    def __getitem__(self, item):
        return self.blocks[item]

    def __init__(self, x: int, y: int, z: int, blockList: [list[Block], None], subRegion: Region, size=16, height=16):
        self.xPos = x
        self.yPos = y
        self.zPos = z
        self.size = size
        self.height = height
        self.blocks = blockList
        if self.blocks is None:
            self.blocks = {}
            for a in range(self.size):
                for b in range(self.height):
                    for c in range(self.size):
                        if b == 0:
                            asyncio.get_event_loop().run_until_complete(self.addNewBlock(a, b, c, Block(a, b, c, "BEDROCK", {})))  # Flat bedrock at y=0
                        else:
                            asyncio.get_event_loop().run_until_complete(self.addNewBlock(a, b, c, Block(a, b, c, "AIR", {})))

    async def addNewBlock(self, x: int, y: int, z: int, block: Block) -> None:
        if x - 1 > self.size or z - 1 > self.size:
            raise Exceptions.OutOfBoundsError(
                "New block location is out of the chunk at {0}, {1}: trying to place a block at {2},"
                "{3} in a {4} block wide chunk!".format(self.xPos, self.zPos, x, z, self.size))
        elif y - 1 > self.height:
            raise Exceptions.OutOfBoundsError("New block location is out of the chunk at {0}, {1}: trying to place a "
                                              "block at y={2} in a {3} block tall chunk!".format(self.xPos,
                                                                                                 self.zPos, y,
                                                                                                 self.height))
        self.blocks["{},{},{}".format(x, y, z)] = block

    def getChunk(self):
        return self
