from classes import BasicClasses
from random import randint, choice

class AbstractTerrainFeature:
    
    def generation_attempt(self, random: float, chunk, chunk_x: int, chunk_y: int, chunk_z: int, is_top_layer: bool):
        pass

class OreFeature(AbstractTerrainFeature):
    
    ore_name: str = "missing"
    chance: float = -1
    max_y: int = -1
    min_y: int = -1
    batch_min = 0
    batch_max = 0
    
    def __init__ (self, ore: str, weight: float, minimum_y: int, maximum_y: int, min_size: int, max_size: int):
        self.ore_name = ore
        self.chance = weight
        self.max_y = maximum_y
        self.min_y = minimum_y
        self.batch_min = min_size
        self.batch_max = max_size
    
    def generation_attempt(self, random: float, chunk, chunk_x: int, chunk_y: int, chunk_z, is_top_layer: bool):
        if is_top_layer:
            pass
        elif random < self.chance and chunk_y < self.max_y and chunk_y > self.min_y:
            blobsize: int = randint(self.batch_min, self.batch_max)
            for x in range(blobsize):
                delta_x: int = round(x/3 + 0.66)
                delta_y: int = round(x/3 + 0.33)
                delta_z: int = round(x/3)
                block_x: int = delta_x + chunk_x + chunk.xPos
                # Danger! Statement below may be victim of misunderstandings
                block_y: int = delta_y + chunk_y + chunk.yPos
                block_z: int = delta_z + chunk_z + chunk.zPos
                chunk.addNewBlock(chunk_x + delta_x, chunk_y + delta_y, chunk_z + delta_z, BasicClasses.Block(block_x, block_y, block_z, self.ore_name, None))
        else:
            pass
class AbstractTreeGenerator(AbstractTerrainFeature):
    
    trunk_name: str = "missing"
    leaf_name: str = "missing"
    chance: float = -1
    max_y: int = -1
    min_y: int = -1
    
    def __init__ (self, trunk: str, leaves: str, weight: float, min_height: int, max_height: int):
        self.trunk_name = trunk
        self.leaf_name = leaves
        self.chance = weight
        self.max_y = max_height
        self.min_y = min_height
    
    def _leaves (self):
        #the Generator for the leaves - only marks their positions, the Generator here is made to copy the generation of birch trees.
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
    
    def generation_attempt(self, random: float, chunk, chunk_x: int, chunk_y: int, chunk_z, is_top_layer: bool):
        if not is_top_layer:
            pass
        elif random < self.chance and chunk_y < self.max_y and chunk_y > self.min_y:
            height: int = round(random()* (self.max_y-self.min_y))+self.min_y
            block_x: int = chunk_x + chunk.xPos
            block_z: int = chunk_z + chunk.zPos
            for delta_y in range(height):#trunk generation
                # Danger! Statement below may be victim of misunderstandings
                block_y: int = delta_y + chunk_y + chunk.yPos
                # TODO trunk orientation
                chunk.addNewBlock(chunk_x, chunk_y + delta_y, chunk_z, BasicClasses.Block(block_x, block_y, block_z, self.trunk_name, None))
            
            blocks = self._leaves()
            for b in blocks:
                # Danger! Statement below may be victim of misunderstandings
                block_y: int = b[1] + chunk_y + chunk.yPos
                block_x = b[0] + chunk_x + chunk.xPos
                block_z = b[2] + chunk_z + chunk.zPos
                chunk.addNewBlock(chunk_x + b[0], chunk_y + b[1], chunk_z + b[2], BasicClasses.Block(block_x, block_y, block_z, self.leaf_name, None))
            
        else:
            pass
