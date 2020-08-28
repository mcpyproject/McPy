import re

from enum import Enum, IntEnum


class Version(Enum):

    def __init__(self, major, minor, version, protocol):
        self.major = major
        self.minor = minor
        self.version = version
        self.protocol = protocol
        self.all = (major, minor, version)

    def is_same_major(self, other_version):
        return self.major == other_version.major

    def get_version(protocol):
        for v in Version:
            if v.protocol == protocol:
                return v
        return None

    def __lt__(self, other):
        if type(other) == tuple:
            return self.all < other
        else:
            return self.all < other.all

    def __le__(self, other):
        return not self.__gt__(other)

    def __eq__(self, other):
        if type(other) == tuple:
            return self.all == other
        else:
            return self.all == other.all

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __gt__(self, other):
        if type(other) == tuple:
            return self.all > other
        else:
            return self.all > other.all

    v1_12_0 = (1, 12, 0, 335)
    v1_12_1 = (1, 12, 1, 338)
    v1_12_2 = (1, 12, 2, 340)
    v1_13_0 = (1, 13, 0, 393)
    v1_13_1 = (1, 13, 1, 401)
    v1_13_2 = (1, 13, 2, 404)
    v1_14_0 = (1, 14, 0, 477)
    v1_14_1 = (1, 14, 1, 480)
    v1_14_2 = (1, 14, 2, 485)
    v1_14_3 = (1, 14, 3, 490)
    v1_14_4 = (1, 14, 4, 498)
    v1_15_0 = (1, 15, 0, 573)
    v1_15_1 = (1, 15, 1, 575)
    v1_15_2 = (1, 15, 2, 578)
    v1_16_0 = (1, 16, 0, 735)
    v1_16_1 = (1, 16, 1, 736)
    v1_16_2 = (1, 16, 2, 751)


class GameMode(IntEnum):

    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3


regex_color = re.compile(r"§[0-9A-FK-OR]", re.IGNORECASE)


class ChatColor(Enum):

    def __init__(self, key, id):
        self.key = key
        self.id = id

    def key():
        return '§'

    def strip_color(input):
        return regex_color.sub('', input)

    def translate_alternate_color(char, text):
        # TODO
        return text

    BLACK = ('0', 0)
    DARK_BLUE = ('1', 1)
    DARK_GREEN = ('2', 2)
    DARK_AQUA = ('3', 3)
    DARK_RED = ('4', 4)
    DARK_PURPLE = ('5', 5)
    GOLD = ('6', 6)
    GRAY = ('7', 7)
    DARK_GRAY = ('8', 8)
    BLUE = ('9', 9)
    GREEN = ('a', 10)
    AQUA = ('b', 11)
    RED = ('c', 12)
    LIGHT_PURPLE = ('d', 13)
    YELLOW = ('e', 14)
    WHITE = ('f', 15)
    MAGIC = ('k', 16)
    BOLD = ('l', 17)
    STRIKETHROUGH = ('m', 18)
    UNDERLINE = ('n', 19)
    ITALIC = ('o', 20)
    RESET = ('r', 21)


class Dimension(Enum):

    OVERWORLD = 1
    NETHER = 2
    THE_END = 3


class Effect(Enum):

    def __init__(self, protocol_id, namespace_id):
        self.id = self.protocol_id = protocol_id
        self.namespace_id = namespace_id

    SPEED = (1, 'speed')
    SLOWNESS = (2, 'slowness')
    HASTE = (3, 'haste')
    MINING_FATIGUE = (4, 'mining_fatigue')
    STRENGTH = (5, 'strength')
    INSTANT_HEALTH = (6, 'instant_health')
    INSTANT_DAMAGE = (7, 'instant_damage')
    JUMP_BOOST = (8, 'jump_boost')
    NAUSEA = (9, 'nausea')
    REGENERATION = (10, 'regeneration')
    RESISTANCE = (11, 'resistance')
    FIRE_RESISTANCE = (12, 'fire_resistance')
    WATER_BREATHING = (13, 'water_breathing')
    INVISIBILITY = (14, 'invisibility')
    BLINDNESS = (15, 'blindness')
    NIGHT_VISION = (16, 'night_vision')
    HUNGER = (17, 'hunger')
    WEAKNESS = (18, 'weakness')
    POISON = (19, 'poison')
    WITHER = (20, 'wither')
    HEALTH_BOOST = (21, 'health_boost')
    ABSORPTION = (22, 'absorption')
    SATURATION = (23, 'saturation')
    GLOWING = (24, 'glowing')
    LEVITATION = (25, 'levitation')
    LUCK = (26, 'luck')
    UNLUCk = (27, 'unluck')
    SLOW_FALLING = (28, 'slow_falling')
    CONDUIT_POWER = (29, 'conduit_power')
    DOLPHINE_GRACE = (30, 'dolphins_grace')
    BAD_OMEN = (31, 'bad_omen')
    HERO_OF_THE_VILLAGE = (32, 'hero_of_the_village')


class Enchantment(Enum):

    def __init__(self, protocol_id, namespace_id):
        self.id = self.protocol_id = protocol_id
        self.namespace_id = namespace_id

    PROTECTION = (0, 'protection')
    FIRE_PROTECTION = (1, 'fire_protection')
    FEATHER_FALLING = (2, 'feather_falling')
    BLAST_PROTECTION = (3, 'blast_protection')
    PROJECTILE_PROTECTION = (4, 'projectile_protection')
    RESPIRATION = (5, 'respiration')
    AQUA_AFFINITY = (6, 'aqua_affinity')
    THORNS = (7, 'thorns')
    DEPTH_STRIDER = (8, 'depth_strider')
    FROST_WALKER = (9, 'frost_walker')
    BINDING_CURSE = (10, 'binding_curse')
    SHARPNESS = (11, 'sharpness')
    SMITE = (12, 'smite')
    BANE_OF_ARTHROPODS = (13, 'bane_of_arthropods')
    KNOCKBACK = (14, 'knockback')
    FIRE_ASPECT = (15, 'fire_aspect')
    LOOTING = (16, 'looting')
    SWEEPING = (17, 'sweeping')
    EFFICIENCY = (18, 'efficiency')
    SILK_TOUCH = (19, 'silk_touch')
    UNBREAKING = (20, 'unbreaking')
    FORTUNE = (21, 'fortune')
    POWER = (22, 'power')
    PUNCH = (23, 'punch')
    FLAME = (24, 'flame')
    INFINITY = (25, 'infinity')
    LUCK_OF_THE_SEA = (26, 'luck_of_the_sea')
    LURE = (27, 'lure')
    LOYALTY = (28, 'loyalty')
    IMPALING = (29, 'impaling')
    RIPTIDE = (30, 'riptide')
    CHANNELING = (31, 'channeling')
    MULTISHOT = (32, 'multishot')
    QUICK_CHARGE = (33, 'quick_charge')
    PIERCING = (34, 'piercing')
    MENDING = (35, 'mending')
    VANISHING_CURSE = (36, 'vanishing_curse')


class Entity(Enum):

    def __init__(self, protocol_id, namespace_id):
        self.id = self.protocol_id = protocol_id
        self.namespace_id = namespace_id

    AREA_EFFECT_CLOUD = (0, 'area_effect_cloud')
    ARMOR_STAND = (1, 'armor_stand')
    ARROW = (2, 'arrow')
    BAT = (3, 'bat')
    BEE = (4, 'bee')
    BLAZE = (5, 'blaze')
    BOAT = (6, 'boat')
    CAT = (7, 'cat')
    CAVE_SPIDER = (8, 'cave_spider')
    CHICKEN = (9, 'chicken')
    COD = (10, 'cod')
    COW = (11, 'cow')
    CREEPER = (12, 'creeper')
    DONKEY = (13, 'donkey')
    DOLPHIN = (14, 'dolphin')
    DRAGON_FIREBALL = (15, 'dragon_fireball')
    DROWNED = (16, 'drowned')
    ELDER_GUARDIAN = (17, 'elder_guardian')
    END_CRYSTAL = (18, 'end_crystal')
    ENDER_DRAGON = (19, 'ender_dragon')
    ENDERMAN = (20, 'enderman')
    ENDERMITE = (21, 'endermite')
    EVOKER_FANGS = (22, 'evoker_fangs')
    EVOKER = (23, 'evoker')
    EXPERIENCE_ORB = (24, 'experience_orb')
    EYE_OF_ENDER = (25, 'eye_of_ender')
    FALLING_BLOCK = (26, 'falling_block')
    FIREWORK_ROCKET = (27, 'firework_rocket')
    FOX = (28, 'fox')
    GHAST = (29, 'ghast')
    GIANT = (30, 'giant')
    GUARDIAN = (31, 'guardian')
    HORSE = (32, 'horse')
    HUSK = (33, 'husk')
    ILLUSIONER = (34, 'illusioner')
    ITEM = (35, 'item')
    ITEM_FRAME = (36, 'item_frame')
    FIREBALL = (37, 'fireball')
    LEASH_KNOT = (38, 'leash_knot')
    LLAMA = (39, 'llama')
    LLAMA_SPIT = (40, 'llama_spit')
    MAGMA_CUBE = (41, 'magma_cube')
    MINECART = (42, 'minecart')
    CHEST_MINECART = (43, 'chest_minecart')
    COMMAND_BLOCK_MINECART = (44, 'command_block_minecart')
    FURNACE_MINECART = (45, 'furnace_minecart')
    HOPPER_MINECART = (46, 'hopper_minecart')
    SPAWNER_MINECART = (47, 'spawner_minecart')
    TNT_MINECART = (48, 'tnt_minecart')
    MULE = (49, 'mule')
    MOOSHROOM = (50, 'mooshroom')
    OCELOT = (51, 'ocelot')
    PAINTING = (52, 'painting')
    PANDA = (53, 'panda')
    PARROT = (54, 'parrot')
    PIG = (55, 'pig')
    PUFFERFISH = (56, 'pufferfish')
    ZOMBIE_PIGMAN = (57, 'zombie_pigman')
    POLAR_BEAR = (58, 'polar_bear')
    TNT = (59, 'tnt')
    RABBIT = (60, 'rabbit')
    SALMON = (61, 'salmon')
    SHEEP = (62, 'sheep')
    SHULKER = (63, 'shulker')
    SHULKER_BULLET = (64, 'shulker_bullet')
    SILVERFISH = (65, 'silverfish')
    SKELETON = (66, 'skeleton')
    SKELETON_HORSE = (67, 'skeleton_horse')
    SLIME = (68, 'slime')
    SMALL_FIREBALL = (69, 'small_fireball')
    SNOW_GOLEM = (70, 'snow_golem')
    SNOWBALL = (71, 'snowball')
    SPECTRAL_ARROW = (72, 'spectral_arrow')
    SPIDER = (73, 'spider')
    SQUID = (74, 'squid')
    STRAY = (75, 'stray')
    TRADER_LLAMA = (76, 'trader_llama')
    TROPICAL_FISH = (77, 'tropical_fish')
    TURTLE = (78, 'turtle')
    EGG = (79, 'egg')
    ENDER_PEARL = (80, 'ender_pearl')
    EXPERIENCE_BOTTLE = (81, 'experience_bottle')
    POTION = (82, 'potion')
    TRIDENT = (83, 'trident')
    VEX = (84, 'vex')
    VILLAGER = (85, 'villager')
    IRON_GOLEM = (86, 'iron_golem')
    VINDICATOR = (87, 'vindicator')
    PILLAGER = (88, 'pillager')
    WANDERING_TRADER = (89, 'wandering_trader')
    WITCH = (90, 'witch')
    WITHER = (91, 'wither')
    WITHER_SKELETON = (92, 'wither_skeleton')
    WITHER_SKULL = (93, 'wither_skull')
    WOLF = (94, 'wolf')
    ZOMBIE = (95, 'zombie')
    ZOMBIE_HORSE = (96, 'zombie_horse')
    ZOMBIE_VILLAGER = (97, 'zombie_villager')
    PHANTOM = (98, 'phantom')
    RAVAGER = (99, 'ravager')
    LIGHTNING_BOLT = (100, 'lightning_bolt')
    PLAYER = (101, 'player')
    FISHING_BOBBER = (102, 'fishing_bobber')
