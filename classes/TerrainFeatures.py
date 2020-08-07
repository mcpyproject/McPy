""" The module descripes Terrain features, which are generators used to generate small structures """

from random import randint, choice

import BasicClasses
from materials import Material


def _generate_block_unsafely(chunk, chunkpos: [int, int, int], pos: [int, int, int], material: Material) -> bool:
    """Generated a block in a given chunk unsafely -> ignores any errors """
    try:
        chunk.addNewBlock(chunkpos[0], chunkpos[1], chunkpos[2], BasicClasses.Block(pos[0], pos[1], pos[2], material, None))
        return True
    except:
        return False


def _generate_block(region: BasicClasses.Region, chunk: BasicClasses.Region, chunkpos: [int, int, int], material: Material):
    """Generates a block safely (Errors may however still occour) by going to a nearby chunk
     If the chunkpos are out of bounds. However, this function uses up more resources"""
    if (chunkpos[0] < 0 or chunkpos[0] > 15 or
       chunkpos[1] < 0 or chunkpos [1] > 15 or
       chunkpos [2] < 0 or chunkpos[2] > 15):
        pass
        #FIXME region.getChunk() is borked
        #walk to the correct chunk
        #c = [chunk.xPos + chunkpos[0]/16, chunk.yPos + chunkpos[1]/16, chunk.zPos + chunkpos[2]/16]
        #this is where we should load the correct chunk
        # however right now that is Not Possible
    _generate_block_unsafely(chunk, chunkpos, [chunk.xPos * 16 + chunkpos[0], chunk.yPos * 16 + chunkpos [1], chunk.zPos * 16 + chunkpos [2]], material)


def _is_air (chunk: BasicClasses.Chunk, x: int, y: int, z: int):
    """ Checks If a Block at a given position relative to the given chunk is air """
    try:
        return chunk.blocks["{},{},{}".format(x, y, z)].get_material().is_air()
    except:
        return True


class AbstractTerrainFeature:
    def generation_attempt(self, chunk_region: BasicClasses.Region, random: float, chunk, chunk_x: int, chunk_y: int, chunk_z: int, is_top_layer: bool):
        pass


class OreFeature(AbstractTerrainFeature):
    
    _ore: Material = Material.AIR
    chance: float = -1
    max_y: int = -1
    min_y: int = -1
    batch_min = 0
    batch_max = 0
    
    def __init__ (self, ore: Material, weight: float, minimum_y: int, maximum_y: int, min_size: int, max_size: int):
        self._ore = ore
        self.chance = weight
        self.max_y = maximum_y
        self.min_y = minimum_y
        self.batch_min = min_size
        self.batch_max = max_size
    
    def generation_attempt(self, chunk_region: BasicClasses.Region, random: float, chunk: BasicClasses.Chunk, chunk_x: int, chunk_y: int, chunk_z, is_top_layer: bool):
        if is_top_layer:
            pass
        elif random < self.chance and self.max_y > chunk_y > self.min_y:
            blobsize: int = randint(self.batch_min, self.batch_max)
            for x in range(blobsize):
                delta_x: int = round(x/3 + 0.66)
                delta_y: int = round(x/3 + 0.33)
                delta_z: int = round(x/3)
                _generate_block(chunk_region, chunk, [chunk_x + delta_x, chunk_y + delta_y, chunk_z + delta_z], self._ore)
        else:
            pass


class AbstractTreeGenerator(AbstractTerrainFeature):
    """Marks a tree Generator, by default it generates a birch-looking tree"""

    _trunk: Material = Material.AIR
    _leaves_mat: Material = Material.AIR
    chance: float = -1
    max_y: int = -1
    min_y: int = -1
    
    def __init__ (self, trunk: Material, leaves: Material, weight: float, min_height: int, max_height: int):
        self._trunk = trunk
        self._leaves_mat = leaves
        self.chance = weight
        self.max_y = max_height
        self.min_y = min_height
    
    def _leaves (self) -> [[int, int, int]]:
        """ The Generator for the leaves; only marks their positions.
        The Generator here is made to copy the generation of birch trees."""
        plot = [[0, 0, 0]]#top trunk block
        for y in (0,-1):# top layers
            plot.extend(([-1, y, 0], [0, y, -1], [0, y, 1], [1, y, 0]))
        #optional leaves at layer 2
        for obj in ([-1, -1, -1], [-1, -1, 1], [1, -1, -1], [1, -1, 1]):
            if choice((True, False)):
                plot.append(obj)
        for y in (-2, -3):
            for x in range(-2, 2):
                for z in range(-2, 2):
                    #filter out optional leaves and trunk
                    if (x == 0 and z == 0) or (abs(x) == 2 and abs(z) == 2):
                        continue
                    else:
                        plot.append([x, y, z])
        #optional leaves at layer 3 and 4
        for y in (-2, -3):
            for obj in ([-2, y, -2], [-2, y, 2], [2, y, -2], [2, y, 2]):
                if choice((True, False)):
                    plot.append(obj)
        return plot
    
    def generation_attempt(self, chunk_region: BasicClasses.Region, random: float, chunk: BasicClasses.Chunk, chunk_x: int, chunk_y: int, chunk_z, is_top_layer: bool):
        if not is_top_layer:
            pass
        elif random < self.chance and self.max_y > chunk_y > self.min_y:
            height: int = randint(self.min_y, self.max_y)
            for delta_y in range(height):#check If it can generate the trunk
                if _is_air(chunk, chunk_x, chunk_y + delta_y, chunk_z):
                    return
            for delta_y in range(height):#trunk generation
                # TODO trunk orientation
                _generate_block(chunk_region, chunk, [chunk_x, chunk_y + delta_y, chunk_z], self._trunk)
                
            blocks = self._leaves()
            for b in blocks:
                pos = [chunk_x + b[0], chunk_y + b[1] + height, chunk_z + b[2]]
                if _is_air(chunk, pos[0], pos[1], pos[2]):
                    continue
                _generate_block(chunk_region, chunk, pos, self._leaves_mat)
        else:
            pass


class MatchstckTreeGenerator(AbstractTreeGenerator):
    """Creates rather tall trees that have not many leaves,
    the shape of the canope leads them to be called Matchstick trees"""
    
    def _leaves(self) -> [[int, int, int]]:
        plot: [[int, int, int]] = [[0, 0, 0]] #top trunk block
        height: int = -(randint(3, 5))
        for y in range(height, -1):
            plot.extend(([-1, y, 0], [0, y, -1], [0, y, 1], [1, y, 0]))
        return plot
