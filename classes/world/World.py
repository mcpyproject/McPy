import numpy as np

from ..blocks.Materials import Material
from ..utils.Utils import Version


class ChunkSection():
    """
    A ChunkSection is a section of a chunk.
    His size is 16x16x16 for a total of 4096 blocks and there is 16 ChunkSections in a Chunk
    """
    # Represent an empty section
    # DO NOT EDIT IT !!!!
    _empty_section = [[[0] * 16] * 16] * 16

    def __init__(self, y, chunk):
        self._y = y
        self._chunk = chunk
        self._load = False
        self._generate = False
        self.generate_empty_section()

    def y(self):
        return self._y

    def chunk(self):
        return self._chunk

    def is_loaded(self):
        return self._load

    def load(self):
        self._load = True

    def unload(self):
        self._load = False

    def is_generated(self):
        return self._generate

    def generate(self):
        self._generate = True

    def blocks(self, blocks):
        self._blocks = blocks
        self.calculate_number_block()

    def get_block(self, x, y, z):
        if y < (self._y * 16) or y > (self._y * 16) + 15:
            return 0
        return self._blocks[x % 16][z % 16][y % 16]

    def set_block(self, x, y, z, id):
        if y < self._y or y > self._y + 15:
            return
        self._blocks[x % 16][z % 16][y % 16] = id
        if id == 0:
            self._number_blocks = self._number_blocks + 1
        else:
            self._number_blocks = self._number_blocks - 1

    def generate_empty_section(self):
        self._blocks = self._empty_section
        self._number_blocks = 0

    def calculate_number_block(self):
        """
        Calculate the number of empty blocks (for now, only check for AIR blocks)
        """
        y = np.array(self._blocks)
        self._number_blocks = np.count_nonzero(y == 0)

    def is_empty(self):
        return self._number_blocks == 0

    def get_number_block(self):
        return self._number_blocks


class Chunk():
    """
    A Chunk is a method used to divide an infinite map.

    it has a size of 16x16x256 for a total of 65536 blocks and is composed of 16 ChunkSection

    It is generated either by a player or by a plugin and his generation is based on a seed
    """

    def __init__(self, x, z, world):
        self._x = x
        self._z = z
        self._world = world
        self._load = False
        self._generate = False
        self._sections = [ChunkSection(y, self) for y in range(16)]

    def x(self):
        return self._x

    def z(self):
        return self._z

    def world(self):
        return self._world

    def is_loaded(self):
        return self._load

    def load(self):
        for section in self._sections:
            section.load()
        self._load = True

    def unload(self):
        for section in self._sections:
            section.unload()
        self._load = False

    def is_generated(self):
        return self._generate

    def generate(self):
        for section in self._sections:
            section.generate()
        self._generate = True

    def set_blocks_at_section(self, y, blocks):
        self._sections[y].blocks(blocks)

    def get_section(self, y):
        if y < 0 or y > 15:
            return None
        return self._sections[y]

    def get_block(self, x, y, z):
        if not self.is_loaded():
            return Material.AIR
        if y < 0 or y > 255:
            return Material.AIR
        section = self.get_section(y / 16)
        if section:
            return section.get_block(x, y, z)

    def set_block(self, x, y, z, id):
        if not self.is_loaded():
            return Material.AIR
        if y < 0 or y > 255:
            return Material.AIR
        section = self.get_section(y / 16)
        if section:
            section.set_block(x, y, z, id)


class World:
    """
    A class that is used to manage a chunk of blocks

    Chunks are composed of blocks and has a size of 16x16x256
    """

    def __init__(self, name, version: Version):
        self._name = name
        self._version = version
        self._chunks = {}

    def name(self):
        return self._name

    def version(self):
        return self._version

    def get_chunk(self, x, z) -> Chunk:
        key_name = '%d_%d' % (x, z)
        if key_name not in self._chunks:
            chunk = Chunk(x, z, self)
            self._chunks[key_name] = chunk
        # Load chunk if not loaded
        chunk = self._chunks[key_name]
        if not chunk.is_loaded():
            self.load_chunk(chunk)
        return chunk

    def load_chunk(self, chunk):
        # Generate if needed
        if not chunk.is_generated():
            self.generate_chunk(chunk)
        chunk.load()

    def generate_chunk(self, chunk: Chunk):
        """
        Generate a chunk or regenerate it if already generated

        Returns True if succesfully generated, False otherwise
        """
        blocks = World._generate_empty_chunk_date()
        # Generate a flat world
        for x in range(16):
            for z in range(16):
                blocks[x][z][0] = 33
                for y in range(1, 5):
                    blocks[x][z][y] = 10
                blocks[x][z][5] = 9
        chunk.blocks(blocks)
        chunk.generate()
        return True

    @staticmethod
    def _generate_empty_chunk_date():
        return [[[0] * 256] * 16] * 16

    def get_block(self, x, y, z):
        chunk = self.get_chunk(x, z)
        return chunk.get_block(x, y, z)

    def set_block(self, x, y, z, id):
        chunk = self.get_chunk(x, z)
        chunk.set_block(x, y, z, id)
