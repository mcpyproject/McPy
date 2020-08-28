# coding=utf-8
from math import floor, sqrt
from random import randint

from .BasicClasses import Block, Chunk, Region
from .TerrainFeatures import AbstractTerrainFeature, AbstractTreeGenerator, MatchstickTreeGenerator, OreFeature
from .blocks.Materials import Material

# Ore height ranges: the lower range will have a higher chance of being selected
# generate coal ore between y=1 and y=128 at vein size between 5 and 16 blocks, at a 3 in 100 chance
COAL_ORE = OreFeature(Material.COAL_ORE, 3, 0, 128, 5, 16)
IRON_ORE = OreFeature(Material.IRON_ORE, 3, 0, 64, 6, 8)
LAPIZ_ORE = OreFeature(Material.LAPIS_ORE, 3, 0, 32, 1, 3)
GOLD_ORE = OreFeature(Material.GOLD_ORE, 3, 0, 32, 6, 8)
REDSTONE_ORE = OreFeature(Material.REDSTONE_ORE, 3, 0, 24, 3, 8)
DIAMOND_ORE = OreFeature(Material.DIAMOND_ORE, 3, 0, 16, 4, 8)

# Trees
BIRCH_TREE = AbstractTreeGenerator(Material.BIRCH_LOG, Material.BIRCH_LEAVES, 0.5, 5, 8)
MATCHSTICK_TREE = MatchstickTreeGenerator(Material.SPRUCE_LOG, Material.SPRUCE_LEAVES, 0.3, 8, 12)
OAK_TREE = AbstractTreeGenerator(Material.OAK_LOG, Material.OAK_LEAVES, 1.5, 4, 8)

# Holds stuff spawning naturally on world Generation - like trees or ores
GENERATORS: [AbstractTerrainFeature] = [COAL_ORE, IRON_ORE, LAPIZ_ORE, GOLD_ORE, REDSTONE_ORE, DIAMOND_ORE, OAK_TREE,
                                        BIRCH_TREE, MATCHSTICK_TREE]


# Cave size settings
WEIRDNESS = 0  # How random should the caves be? Lower values = short but very twisty: high values = long but very
# straight: constrained to between -1 and 1

# 3D Gradient vectors
_GRAD3 = ((1, 1, 0), (-1, 1, 0), (1, -1, 0), (-1, -1, 0),
          (1, 0, 1), (-1, 0, 1), (1, 0, -1), (-1, 0, -1),
          (0, 1, 1), (0, -1, 1), (0, 1, -1), (0, -1, -1),
          (1, 1, 0), (0, -1, 1), (-1, 1, 0), (0, -1, -1),
          )

# 4D Gradient vectors
_GRAD4 = ((0, 1, 1, 1), (0, 1, 1, -1), (0, 1, -1, 1), (0, 1, -1, -1),
          (0, -1, 1, 1), (0, -1, 1, -1), (0, -1, -1, 1), (0, -1, -1, -1),
          (1, 0, 1, 1), (1, 0, 1, -1), (1, 0, -1, 1), (1, 0, -1, -1),
          (-1, 0, 1, 1), (-1, 0, 1, -1), (-1, 0, -1, 1), (-1, 0, -1, -1),
          (1, 1, 0, 1), (1, 1, 0, -1), (1, -1, 0, 1), (1, -1, 0, -1),
          (-1, 1, 0, 1), (-1, 1, 0, -1), (-1, -1, 0, 1), (-1, -1, 0, -1),
          (1, 1, 1, 0), (1, 1, -1, 0), (1, -1, 1, 0), (1, -1, -1, 0),
          (-1, 1, 1, 0), (-1, 1, -1, 0), (-1, -1, 1, 0), (-1, -1, -1, 0))

# A lookup table to traverse the simplex around a given point in 4D.
# Details can be found where this table is used, in the 4D noise method.
_SIMPLEX = (
    (0, 1, 2, 3), (0, 1, 3, 2), (0, 0, 0, 0), (0, 2, 3, 1), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (1, 2, 3, 0),
    (0, 2, 1, 3), (0, 0, 0, 0), (0, 3, 1, 2), (0, 3, 2, 1), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (1, 3, 2, 0),
    (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0),
    (1, 2, 0, 3), (0, 0, 0, 0), (1, 3, 0, 2), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (2, 3, 0, 1), (2, 3, 1, 0),
    (1, 0, 2, 3), (1, 0, 3, 2), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (2, 0, 3, 1), (0, 0, 0, 0), (2, 1, 3, 0),
    (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0),
    (2, 0, 1, 3), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (3, 0, 1, 2), (3, 0, 2, 1), (0, 0, 0, 0), (3, 1, 2, 0),
    (2, 1, 0, 3), (0, 0, 0, 0), (0, 0, 0, 0), (0, 0, 0, 0), (3, 1, 0, 2), (0, 0, 0, 0), (3, 2, 0, 1), (3, 2, 1, 0))

# Simplex skew constants
_F2 = 0.5 * (sqrt(3.0) - 1.0)
_G2 = (3.0 - sqrt(3.0)) / 6.0
_F3 = 1.0 / 3.0
_G3 = 1.0 / 6.0


def scaleNoise(noise: float, limit: tuple) -> float:
    upperLimit = int(limit[0])
    lowerLimit = int(limit[1])
    return (noise + 1) / 2 * (upperLimit - lowerLimit) + lowerLimit


class BaseNoise:
    """Noise abstract base class"""

    permutation = (151, 160, 137, 91, 90, 15,
                   131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37, 240, 21, 10, 23,
                   190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57, 177, 33,
                   88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166,
                   77, 146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244,
                   102, 143, 54, 65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196,
                   135, 130, 116, 188, 159, 86, 164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123,
                   5, 202, 38, 147, 118, 126, 255, 82, 85, 212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42,
                   223, 183, 170, 213, 119, 248, 152, 2, 44, 154, 163, 70, 221, 153, 101, 155, 167, 43, 172, 9,
                   129, 22, 39, 253, 9, 98, 108, 110, 79, 113, 224, 232, 178, 185, 112, 104, 218, 246, 97, 228,
                   251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145, 235, 249, 14, 239, 107,
                   49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4, 150, 254,
                   138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180)

    period = len(permutation)

    # Double permutation array so we don't need to wrap
    permutation *= 2

    randint_function = randint

    def __init__(self, period=None, permutation_table=None, randint_function=None):
        """Initialize the noise generator. With no arguments, the default
        period and permutation table are used (256). The default permutation
        table generates the exact same noise pattern each time.

        An integer period can be specified, to generate a random permutation
        table with period elements. The period determines the (integer)
        interval that the noise repeats, which is useful for creating tiled
        textures.  period should be a power-of-two, though this is not
        enforced. Note that the speed of the noise algorithm is indpendent of
        the period size, though larger periods mean a larger table, which
        consume more memory.

        A permutation table consisting of an iterable sequence of whole
        numbers can be specified directly. This should have a power-of-two
        length. Typical permutation tables are a sequnce of unique integers in
        the range [0,period) in random order, though other arrangements could
        prove useful, they will not be "pure" simplex noise. The largest
        element in the sequence must be no larger than period-1.

        period and permutation_table may not be specified together.

        A substitute for the method random.randint(a, b) can be chosen. The
        method must take two integer parameters a and b and return an integer N
        such that a <= N <= b.
        """
        if randint_function is not None:  # do this before calling randomize()
            if not hasattr(randint_function, '__call__'):
                raise TypeError(
                    'randint_function has to be a function')
            self.randint_function = randint_function
            if period is None:
                period = self.period  # enforce actually calling randomize()
        if period is not None and permutation_table is not None:
            raise ValueError(
                'Can specify either period or permutation_table, not both')
        if period is not None:
            self.randomize(period)
        elif permutation_table is not None:
            self.permutation = tuple(permutation_table) * 2
            self.period = len(permutation_table)

    def randomize(self, period=None):
        """Randomize the permutation table used by the noise functions. This
        makes them generate a different noise pattern for the same inputs.
        """
        if period is not None:
            self.period = period
        perm = list(range(self.period))
        perm_right = self.period - 1
        for i in list(perm):
            j = self.randint_function(0, perm_right)
            perm[i], perm[j] = perm[j], perm[i]
        self.permutation = tuple(perm) * 2


class SimplexNoise(BaseNoise):
    """Perlin simplex noise generator

    Adapted from Stefan Gustavson's Java implementation described here:

    http://staffwww.itn.liu.se/~stegu/simplexnoise/simplexnoise.pdf

    To summarize:

    "In 2001, Ken Perlin presented 'simplex noise', a replacement for his classic
    noise algorithm.  Classic 'Perlin noise' won him an academy award and has
    become an ubiquitous procedural primitive for computer graphics over the
    years, but in hindsight it has quite a few limitations.  Ken Perlin himself
    designed simplex noise specifically to overcome those limitations, and he
    spent a lot of good thinking on it. Therefore, it is a better idea than his
    original algorithm. A few of the more prominent advantages are:

    * Simplex noise has a lower computational complexity and requires fewer
      multiplications.
    * Simplex noise scales to higher dimensions (4D, 5D and up) with much less
      computational cost, the complexity is O(N) for N dimensions instead of
      the O(2^N) of classic Noise.
    * Simplex noise has no noticeable directional artifacts.  Simplex noise has
      a well-defined and continuous gradient everywhere that can be computed
      quite cheaply.
    * Simplex noise is easy to implement in hardware."
    """

    def noise2(self, x, y):
        """2D Perlin simplex noise.

        Return a floating point value from -1 to 1 for the given x, y coordinate.
        The same value is always returned for a given x, y pair unless the
        permutation table changes (see randomize above).
        """
        # Skew input space to determine which simplex (triangle) we are in
        s = (x + y) * _F2
        i = floor(x + s)
        j = floor(y + s)
        t = (i + j) * _G2
        x0 = x - (i - t)  # "Unskewed" distances from cell origin
        y0 = y - (j - t)

        if x0 > y0:
            i1 = 1
            j1 = 0  # Lower triangle, XY order: (0,0)->(1,0)->(1,1)
        else:
            i1 = 0
            j1 = 1  # Upper triangle, YX order: (0,0)->(0,1)->(1,1)

        x1 = x0 - i1 + _G2  # Offsets for middle corner in (x,y) unskewed coords
        y1 = y0 - j1 + _G2
        x2 = x0 + _G2 * 2.0 - 1.0  # Offsets for last corner in (x,y) unskewed coords
        y2 = y0 + _G2 * 2.0 - 1.0

        # Determine hashed gradient indices of the three simplex corners
        perm = self.permutation
        ii = int(i) % self.period
        jj = int(j) % self.period
        gi0 = perm[ii + perm[jj]] % 12
        gi1 = perm[ii + i1 + perm[jj + j1]] % 12
        gi2 = perm[ii + 1 + perm[jj + 1]] % 12

        # Calculate the contribution from the three corners
        tt = 0.5 - x0 ** 2 - y0 ** 2
        if tt > 0:
            g = _GRAD3[gi0]
            noise = tt ** 4 * (g[0] * x0 + g[1] * y0)
        else:
            noise = 0.0

        tt = 0.5 - x1 ** 2 - y1 ** 2
        if tt > 0:
            g = _GRAD3[gi1]
            noise += tt ** 4 * (g[0] * x1 + g[1] * y1)

        tt = 0.5 - x2 ** 2 - y2 ** 2
        if tt > 0:
            g = _GRAD3[gi2]
            noise += tt ** 4 * (g[0] * x2 + g[1] * y2)

        return noise * 70.0  # scale noise to [-1, 1]

    def noise3(self, x, y, z):
        """3D Perlin simplex noise.

        Return a floating point value from -1 to 1 for the given x, y, z coordinate.
        The same value is always returned for a given x, y, z pair unless the
        permutation table changes (see randomize above).
        """
        # Skew the input space to determine which simplex cell we're in
        s = (x + y + z) * _F3
        i = floor(x + s)
        j = floor(y + s)
        k = floor(z + s)
        t = (i + j + k) * _G3
        x0 = x - (i - t)  # "Unskewed" distances from cell origin
        y0 = y - (j - t)
        z0 = z - (k - t)

        # For the 3D case, the simplex shape is a slightly irregular tetrahedron.
        # Determine which simplex we are in.
        if x0 >= y0:
            if y0 >= z0:
                i1 = 1
                j1 = 0
                k1 = 0
                i2 = 1
                j2 = 1
                k2 = 0
            elif x0 >= z0:
                i1 = 1
                j1 = 0
                k1 = 0
                i2 = 1
                j2 = 0
                k2 = 1
            else:
                i1 = 0
                j1 = 0
                k1 = 1
                i2 = 1
                j2 = 0
                k2 = 1
        else:  # x0 < y0
            if y0 < z0:
                i1 = 0
                j1 = 0
                k1 = 1
                i2 = 0
                j2 = 1
                k2 = 1
            elif x0 < z0:
                i1 = 0
                j1 = 1
                k1 = 0
                i2 = 0
                j2 = 1
                k2 = 1
            else:
                i1 = 0
                j1 = 1
                k1 = 0
                i2 = 1
                j2 = 1
                k2 = 0

        # Offsets for remaining corners
        x1 = x0 - i1 + _G3
        y1 = y0 - j1 + _G3
        z1 = z0 - k1 + _G3
        x2 = x0 - i2 + 2.0 * _G3
        y2 = y0 - j2 + 2.0 * _G3
        z2 = z0 - k2 + 2.0 * _G3
        x3 = x0 - 1.0 + 3.0 * _G3
        y3 = y0 - 1.0 + 3.0 * _G3
        z3 = z0 - 1.0 + 3.0 * _G3

        # Calculate the hashed gradient indices of the four simplex corners
        perm = self.permutation
        ii = int(i) % self.period
        jj = int(j) % self.period
        kk = int(k) % self.period
        gi0 = perm[ii + perm[jj + perm[kk]]] % 12
        gi1 = perm[ii + i1 + perm[jj + j1 + perm[kk + k1]]] % 12
        gi2 = perm[ii + i2 + perm[jj + j2 + perm[kk + k2]]] % 12
        gi3 = perm[ii + 1 + perm[jj + 1 + perm[kk + 1]]] % 12

        # Calculate the contribution from the four corners
        noise = 0.0
        tt = 0.6 - x0 ** 2 - y0 ** 2 - z0 ** 2
        if tt > 0:
            g = _GRAD3[gi0]
            noise = tt ** 4 * (g[0] * x0 + g[1] * y0 + g[2] * z0)
        else:
            noise = 0.0

        tt = 0.6 - x1 ** 2 - y1 ** 2 - z1 ** 2
        if tt > 0:
            g = _GRAD3[gi1]
            noise += tt ** 4 * (g[0] * x1 + g[1] * y1 + g[2] * z1)

        tt = 0.6 - x2 ** 2 - y2 ** 2 - z2 ** 2
        if tt > 0:
            g = _GRAD3[gi2]
            noise += tt ** 4 * (g[0] * x2 + g[1] * y2 + g[2] * z2)

        tt = 0.6 - x3 ** 2 - y3 ** 2 - z3 ** 2
        if tt > 0:
            g = _GRAD3[gi3]
            noise += tt ** 4 * (g[0] * x3 + g[1] * y3 + g[2] * z3)

        return noise * 32.0


class WorldGenerator(SimplexNoise):
    
    async def generateNewChunk(self, x, y, z, width, height, region) -> Chunk:
        positions = []
        for blockX in range(1, width):
            for blockZ in range(1, width):
                bY = self.noise2(blockX, blockZ)  # Use 2D noise to generate the y coordinate, then use 3D noise to
                # generate everything else
                blockY = scaleNoise(bY, (63, 80))  # Scale the noise to be between min-max y value
                positions.append((blockX, blockY, blockZ))
        chunk = Chunk(x, y, z, [], region, width, height)
        await self._regenerate_chunk(x, y, z, region, positions, chunk)
        return chunk

    async def _regenerate_chunk(self, x, y, z, region, positions, chunk: Chunk):
        for x, y, z in positions:
            if y < chunk.height*chunk.yPos:
                continue
            if y > chunk.height*(chunk.yPos+1)-1:
                break
            noise = self.noise3(x, y, z)
            for stone in range(y-6, 1):  # Generate stone from 6 below the top layer, to y=1
                await chunk.addNewBlock(x, stone, z, Block(x, stone, z, Material.STONE, {}))
            for dirt in range(y - 1, y - 6):  # Generate dirt from the top layer of stone, to one block below the surface
                await chunk.addNewBlock(x, dirt, z, Block(x, dirt, z, Material.DIRT, {}))
            await chunk.addNewBlock(x, y, z, Block(x, y, z, Material.GRASS_BLOCK, {}))  # Generate grass at the top layer
            for height in range(1, y-6):  # Randomly add ores
                for gen in GENERATORS:
                    gen.generation_attempt(region, scaleNoise(noise, (1, 100)), chunk, x, height, z, False)
            for gen in GENERATORS:
                gen.generation_attempt(region, scaleNoise(noise, (1, 100)), chunk, x, y + 1, z, True)
