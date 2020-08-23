from enum import Enum


class Biome(Enum):

    def __init__(self, id, string):
        self.id = id
        self.string = string

    def id_to_biome(id):
        for biome in Biome:
            if biome.id == id:
                return biome
        return None

    def name_to_biome(name):
        for biome in Biome:
            if biome.name == name:
                return biome
        return None

    def string_to_biome(string):
        for biome in Biome:
            if biome.biome == string:
                return biome
        return None

    OCEAN = (0, 'ocean')
    PLAINS = (1, 'plains')
    DESERT = (2, 'desert')
    MOUNTAINS = (3, 'mountains')
    EXTREME_HILLS = MOUNTAINS
    FOREST = (4, 'forest')
    TAIGA = (5, 'taiga')
    SWAMPLAND = (6, 'swamp')
    RIVER = (7, 'river')
    HELL = (8, 'nether_wastes')
    NETHER = HELL
    SKY = (9, 'the_end')
    END = SKY
    FROZEN_OCEAN = (10, 'frozen_ocean')
    FROZEN_RIVER = (11, 'frozen_river')
    ICE_PLAINS = (12, 'snowy_tundra')
    TUNDRA = ICE_PLAINS
    ICE_MOUNTAINS = (13, 'snowy_mountains')
    MUSHROOM_ISLAND = (14, 'mushroom_fields')
    MUSHROOM_SHORE = (15, 'mushroom_field_shore')
    BEACH = (16, 'beach')
    DESERT_HILLS = (17, 'desert_hills')
    FOREST_HILLS = (18, 'wooded_hills')
    TAIGA_HILLS = (19, 'taiga_hills')
    EXTREME_HILLS_EDGE = (20, 'mountain_edge')
    MOUNTAIN_EDGE = EXTREME_HILLS_EDGE
    JUNGLE = (21, 'jungle')
    JUNGLE_HILLS = (22, 'jungle_hills')
    JUNGLE_EDGE = (23, 'jungle_edge')
    DEEP_OCEAN = (24, 'deep_ocean')
    STONE_BEACH = (25, 'stone_shore')
    COLD_BEACH = (26, 'snowy_beach')
    SNOWY_BEACH = COLD_BEACH
    BIRCH_FOREST = (27, 'birch_forest')
    BIRCH_FOREST_HILLS = (28, 'birch_forest_hills')
    ROOFED_FOREST = (29, 'dark_forest')
    DARK_FOREST = ROOFED_FOREST
    COLD_TAIGA = (30, 'snowy_taiga')
    COLD_TAIGA_HILLS = (31, 'snowy_taiga_hills')
    MEGA_TAIGA = (32, 'giant_tree_taiga')
    MEGA_TAIGA_HILLS = (33, 'giant_tree_taiga_hills')
    EXTREME_HILLS_PLUS = (34, 'wooded_mountains')
    SAVANNA = (35, 'savanna')
    SAVANNA_PLATEAU = (36, 'savanna_plateau')
    MESA = (37, 'badlands')
    BADLANDS = MESA
    MESA_PLATEAU_F = (38, 'wooded_badlands_plateau')
    WOODED_BADLANDS_PLATEAU = MESA_PLATEAU_F
    MESA_PLATEAU = (39, 'MesaPlateau')
    BADLANGS_PLATEAU = MESA_PLATEAU
    SMALL_END_ISLANDS = (40, 'small_end_islands')
    END_MIDLANDS = (41, 'end_midlands')
    END_HIGHLANDS = (42, 'end_highlands')
    END_BARRENS = (43, 'end_barrens')
    WARN_OCEAN = (44, 'warm_ocean')
    LUKEWARM_OCEAN = (45, 'lukewarm_ocean')
    COLD_OCEAN = (46, 'cold_ocean')
    DEEP_WARM_OCEAN = (47, 'deep_warm_ocean')
    DEEP_LUKEWARM_OCEAN = (48, 'deep_lukewarm_ocean')
    DEEP_COLD_OCEAN = (49, 'deep_cold_ocean')
    DEEP_FROZEN_OCEAN = (50, 'deep_frozen_ocean')

    THE_VOID = (127, 'the_void')
    INVALID_BIOME = THE_VOID

    # Variant
    SUNFLOWER_PLAINS = (129, 'sunflower_plains')
    DESERT_LAKES = (130, 'desert_lakes')
    EXTREME_HILLS_M = (131, 'gravelly_mountains')
    GRAVELLY_MOUNTAINS = EXTREME_HILLS_M
    FLOWER_FOREST = (132, 'flower_forest')
    TAIGA_M = (133, 'taiga_mountains')
    TAIGA_MOUNTAINS = TAIGA_M
    SWAMPLAND_M = (134, 'swamp_hills')
    SWAMP_HILLS = SWAMPLAND_M
    ICE_PLAINS_SPIKES = (140, 'ice_spikes')
    JUNGLE_M = (149, 'modified_jungle')
    MODIFIED_JUNGLE = JUNGLE_M
    JUNGLE_EDGE_M = (151, 'modified_jungle_edge')
    MODIFIED_JUNGLE_EDGE = JUNGLE_EDGE_M
    BIRCH_FOREST_M = (155, 'tall_birch_forest')
    TALL_BIRCH_FOREST = BIRCH_FOREST_M
    BIRCH_FOREST_HILLS_M = (156, 'tall_birch_hills')
    TALL_BIRCH_HILLS = BIRCH_FOREST_HILLS_M
    ROOFED_FOREST_M = (157, 'dark_forest_hills')
    DARK_FOREST_HILLS = ROOFED_FOREST_M
    COLD_TAIGA_M = (158, 'snowy_taiga_mountains')
    SNOWY_TAIGA_MOUNTAINS = COLD_TAIGA_M
    GIANT_SPRUCE_TAIGA = (160, 'giant_spruce_taiga')
    GIANT_SPRUCE_TAIGA_HILLS = (161, 'giant_spruce_taiga_hills')
    EXTREME_HILLS_PLUS_M = (162, 'modified_gravelly_mountains')
    MODIFIED_GRAVELLY_MOUNTAINS = EXTREME_HILLS_PLUS_M
    SAVANNA_M = (163, 'shattered_savanna')
    SHATTARED_SAVANNA = SAVANNA_M
    SAVANNA_PLATEAU_M = (164, 'shattered_savanna_plateau')
    SHATTARED_SAVANNA_PLATEAU = SAVANNA_PLATEAU_M
    MESA_BRYCE = (165, 'eroded_badlands')
    ERODED_BADLANGS = MESA_BRYCE
    MESA_PLATEAU_FM = (166, 'modified_wooded_badlands_plateau')
    MODIFIED_WOODED_BADLANDS_PLATEAU = MESA_PLATEAU_FM
    MESA_PLATEAU_M = (167, 'modified_badlands_plateau')
    MODIFIED_BADLANDS_PLATEAU = MESA_PLATEAU_M
    BAMBOO_JUNGLE = (168, 'bamboo_jungle')
    BAMBOO_JUNGLE_HILLS = (169, 'bamboo_jungle_hills')

    # 1.16
    SOUL_SAND_VALLEY = (170, 'soul_sand_valley')
    CRIMSON_FOREST = (171, 'crimson_forest')
    WARPED_FOREST = (172, 'warped_forest')
    BASALT_DELTAS = (173, 'basalt_deltas')
