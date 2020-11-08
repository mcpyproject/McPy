from enum import Enum

from classes.datafile.Parser import Parser


@Parser.Parser(
    file='registries.json',
    directory='data/minecraft/{version}/reports',
    struct={
        'protocol_id': {
            '_action': {
                'type': 'save',
                'id': 'protocol_id',
            },
        },
    },
    array_path='minecraft:biome/entries',
    key_pattern='minecraft:{key}',
)
class Biome(Enum):

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    @staticmethod
    def namespace_to_biome(id):
        for biome in Biome:
            if biome.namespace_id == id:
                return biome
        return None

    OCEAN = ('ocean')
    PLAINS = ('plains')
    DESERT = ('desert')
    MOUNTAINS = ('mountains')
    EXTREME_HILLS = MOUNTAINS
    FOREST = ('forest')
    TAIGA = ('taiga')
    SWAMPLAND = ('swamp')
    RIVER = ('river')
    HELL = ('nether_wastes')
    NETHER = HELL
    SKY = ('the_end')
    END = SKY
    FROZEN_OCEAN = ('frozen_ocean')
    FROZEN_RIVER = ('frozen_river')
    ICE_PLAINS = ('snowy_tundra')
    TUNDRA = ICE_PLAINS
    ICE_MOUNTAINS = ('snowy_mountains')
    MUSHROOM_ISLAND = ('mushroom_fields')
    MUSHROOM_SHORE = ('mushroom_field_shore')
    BEACH = ('beach')
    DESERT_HILLS = ('desert_hills')
    FOREST_HILLS = ('wooded_hills')
    TAIGA_HILLS = ('taiga_hills')
    EXTREME_HILLS_EDGE = ('mountain_edge')
    MOUNTAIN_EDGE = EXTREME_HILLS_EDGE
    JUNGLE = ('jungle')
    JUNGLE_HILLS = ('jungle_hills')
    JUNGLE_EDGE = ('jungle_edge')
    DEEP_OCEAN = ('deep_ocean')
    STONE_BEACH = ('stone_shore')
    COLD_BEACH = ('snowy_beach')
    SNOWY_BEACH = COLD_BEACH
    BIRCH_FOREST = ('birch_forest')
    BIRCH_FOREST_HILLS = ('birch_forest_hills')
    ROOFED_FOREST = ('dark_forest')
    DARK_FOREST = ROOFED_FOREST
    COLD_TAIGA = ('snowy_taiga')
    COLD_TAIGA_HILLS = ('snowy_taiga_hills')
    MEGA_TAIGA = ('giant_tree_taiga')
    MEGA_TAIGA_HILLS = ('giant_tree_taiga_hills')
    EXTREME_HILLS_PLUS = ('wooded_mountains')
    SAVANNA = ('savanna')
    SAVANNA_PLATEAU = ('savanna_plateau')
    MESA = ('badlands')
    BADLANDS = MESA
    MESA_PLATEAU_F = ('wooded_badlands_plateau')
    WOODED_BADLANDS_PLATEAU = MESA_PLATEAU_F
    MESA_PLATEAU = ('MesaPlateau')
    BADLANGS_PLATEAU = MESA_PLATEAU
    SMALL_END_ISLANDS = ('small_end_islands')
    END_MIDLANDS = ('end_midlands')
    END_HIGHLANDS = ('end_highlands')
    END_BARRENS = ('end_barrens')
    WARN_OCEAN = ('warm_ocean')
    LUKEWARM_OCEAN = ('lukewarm_ocean')
    COLD_OCEAN = ('cold_ocean')
    DEEP_WARM_OCEAN = ('deep_warm_ocean')
    DEEP_LUKEWARM_OCEAN = ('deep_lukewarm_ocean')
    DEEP_COLD_OCEAN = ('deep_cold_ocean')
    DEEP_FROZEN_OCEAN = ('deep_frozen_ocean')

    THE_VOID = ('the_void')
    INVALID_BIOME = THE_VOID

    # Variant
    SUNFLOWER_PLAINS = ('sunflower_plains')
    DESERT_LAKES = ('desert_lakes')
    EXTREME_HILLS_M = ('gravelly_mountains')
    GRAVELLY_MOUNTAINS = EXTREME_HILLS_M
    FLOWER_FOREST = ('flower_forest')
    TAIGA_M = ('taiga_mountains')
    TAIGA_MOUNTAINS = TAIGA_M
    SWAMPLAND_M = ('swamp_hills')
    SWAMP_HILLS = SWAMPLAND_M
    ICE_PLAINS_SPIKES = ('ice_spikes')
    JUNGLE_M = ('modified_jungle')
    MODIFIED_JUNGLE = JUNGLE_M
    JUNGLE_EDGE_M = ('modified_jungle_edge')
    MODIFIED_JUNGLE_EDGE = JUNGLE_EDGE_M
    BIRCH_FOREST_M = ('tall_birch_forest')
    TALL_BIRCH_FOREST = BIRCH_FOREST_M
    BIRCH_FOREST_HILLS_M = ('tall_birch_hills')
    TALL_BIRCH_HILLS = BIRCH_FOREST_HILLS_M
    ROOFED_FOREST_M = ('dark_forest_hills')
    DARK_FOREST_HILLS = ROOFED_FOREST_M
    COLD_TAIGA_M = ('snowy_taiga_mountains')
    SNOWY_TAIGA_MOUNTAINS = COLD_TAIGA_M
    GIANT_SPRUCE_TAIGA = ('giant_spruce_taiga')
    GIANT_SPRUCE_TAIGA_HILLS = ('giant_spruce_taiga_hills')
    EXTREME_HILLS_PLUS_M = ('modified_gravelly_mountains')
    MODIFIED_GRAVELLY_MOUNTAINS = EXTREME_HILLS_PLUS_M
    SAVANNA_M = ('shattered_savanna')
    SHATTARED_SAVANNA = SAVANNA_M
    SAVANNA_PLATEAU_M = ('shattered_savanna_plateau')
    SHATTARED_SAVANNA_PLATEAU = SAVANNA_PLATEAU_M
    MESA_BRYCE = ('eroded_badlands')
    ERODED_BADLANDS = MESA_BRYCE
    MESA_PLATEAU_FM = ('modified_wooded_badlands_plateau')
    MODIFIED_WOODED_BADLANDS_PLATEAU = MESA_PLATEAU_FM
    MESA_PLATEAU_M = ('modified_badlands_plateau')
    MODIFIED_BADLANDS_PLATEAU = MESA_PLATEAU_M
    BAMBOO_JUNGLE = ('bamboo_jungle')
    BAMBOO_JUNGLE_HILLS = ('bamboo_jungle_hills')

    # 1.16
    SOUL_SAND_VALLEY = ('soul_sand_valley')
    CRIMSON_FOREST = ('crimson_forest')
    WARPED_FOREST = ('warped_forest')
    BASALT_DELTAS = ('basalt_deltas')
