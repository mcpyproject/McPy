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


class Color(Enum):

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

    def __init__(self, protocol_id, id):
        self.protocol_id = protocol_id
        self.id = id

    SPEED = (1, 'minecraft:speed')
    SLOWNESS = (2, 'minecraft:slowness')
    HASTE = (3, 'minecraft:haste')
    MINING_FATIGUE = (4, 'minecraft:mining_fatigue')
    STRENGTH = (5, 'minecraft:strength')
    INSTANT_HEALTH = (6, 'minecraft:instant_health')
    INSTANT_DAMAGE = (7, 'minecraft:instant_damage')
    JUMP_BOOST = (8, 'minecraft:jump_boost')
    NAUSEA = (9, 'minecraft:nausea')
    REGENERATION = (10, 'minecraft:regeneration')
    RESISTANCE = (11, 'minecraft:resistance')
    FIRE_RESISTANCE = (12, 'minecraft:fire_resistance')
    WATER_BREATHING = (13, 'minecraft:water_breathing')
    INVISIBILITY = (14, 'minecraft:invisibility')
    BLINDNESS = (15, 'minecraft:blindness')
    NIGHT_VISION = (16, 'minecraft:night_vision')
    HUNGER = (17, 'minecraft:hunger')
    WEAKNESS = (18, 'minecraft:weakness')
    POISON = (19, 'minecraft:poison')
    WITHER = (20, 'minecraft:wither')
    HEALTH_BOOST = (21, 'minecraft:health_boost')
    ABSORPTION = (22, 'minecraft:absorption')
    SATURATION = (23, 'minecraft:saturation')
    GLOWING = (24, 'minecraft:glowing')
    LEVITATION = (25, 'minecraft:levitation')
    LUCK = (26, 'minecraft:luck')
    UNLUCk = (27, 'minecraft:unluck')
    SLOW_FALLING = (28, 'minecraft:slow_falling')
    CONDUIT_POWER = (29, 'minecraft:conduit_power')
    DOLPHINE_GRACE = (30, 'minecraft:dolphins_grace')
    BAD_OMEN = (31, 'minecraft:bad_omen')
    HERO_OF_THE_VILLAGE = (32, 'minecraft:hero_of_the_village')


class Enchantment(Enum):

    def __init__(self, protocol_id, id):
        self.protocol_id = protocol_id
        self.id = id

    PROTECTION = (0, 'minecraft:protection')
    FIRE_PROTECTION = (1, 'minecraft:fire_protection')
    FEATHER_FALLING = (2, 'minecraft:feather_falling')
    BLAST_PROTECTION = (3, 'minecraft:blast_protection')
    PROJECTILE_PROTECTION = (4, 'minecraft:projectile_protection')
    RESPIRATION = (5, 'minecraft:respiration')
    AQUA_AFFINITY = (6, 'minecraft:aqua_affinity')
    THORNS = (7, 'minecraft:thorns')
    DEPTH_STRIDER = (8, 'minecraft:depth_strider')
    FROST_WALKER = (9, 'minecraft:frost_walker')
    BINDING_CURSE = (10, 'minecraft:binding_curse')
    SHARPNESS = (11, 'minecraft:sharpness')
    SMITE = (12, 'minecraft:smite')
    BANE_OF_ARTHROPODS = (13, 'minecraft:bane_of_arthropods')
    KNOCKBACK = (14, 'minecraft:knockback')
    FIRE_ASPECT = (15, 'minecraft:fire_aspect')
    LOOTING = (16, 'minecraft:looting')
    SWEEPING = (17, 'minecraft:sweeping')
    EFFICIENCY = (18, 'minecraft:efficiency')
    SILK_TOUCH = (19, 'minecraft:silk_touch')
    UNBREAKING = (20, 'minecraft:unbreaking')
    FORTUNE = (21, 'minecraft:fortune')
    POWER = (22, 'minecraft:power')
    PUNCH = (23, 'minecraft:punch')
    FLAME = (24, 'minecraft:flame')
    INFINITY = (25, 'minecraft:infinity')
    LUCK_OF_THE_SEA = (26, 'minecraft:luck_of_the_sea')
    LURE = (27, 'minecraft:lure')
    LOYALTY = (28, 'minecraft:loyalty')
    IMPALING = (29, 'minecraft:impaling')
    RIPTIDE = (30, 'minecraft:riptide')
    CHANNELING = (31, 'minecraft:channeling')
    MULTISHOT = (32, 'minecraft:multishot')
    QUICK_CHARGE = (33, 'minecraft:quick_charge')
    PIERCING = (34, 'minecraft:piercing')
    MENDING = (35, 'minecraft:mending')
    VANISHING_CURSE = (36, 'minecraft:vanishing_curse')


class Entity(Enum):

    def __init__(self, protocol_id, id):
        self.protocol_id = protocol_id
        self.id = id

    AREA_EFFECT_CLOUD = (0, 'minecraft:area_effect_cloud')
    ARMOR_STAND = (1, 'minecraft:armor_stand')
    ARROW = (2, 'minecraft:arrow')
    BAT = (3, 'minecraft:bat')
    BEE = (4, 'minecraft:bee')
    BLAZE = (5, 'minecraft:blaze')
    BOAT = (6, 'minecraft:boat')
    CAT = (7, 'minecraft:cat')
    CAVE_SPIDER = (8, 'minecraft:cave_spider')
    CHICKEN = (9, 'minecraft:chicken')
    COD = (10, 'minecraft:cod')
    COW = (11, 'minecraft:cow')
    CREEPER = (12, 'minecraft:creeper')
    DONKEY = (13, 'minecraft:donkey')
    DOLPHIN = (14, 'minecraft:dolphin')
    DRAGON_FIREBALL = (15, 'minecraft:dragon_fireball')
    DROWNED = (16, 'minecraft:drowned')
    ELDER_GUARDIAN = (17, 'minecraft:elder_guardian')
    END_CRYSTAL = (18, 'minecraft:end_crystal')
    ENDER_DRAGON = (19, 'minecraft:ender_dragon')
    ENDERMAN = (20, 'minecraft:enderman')
    ENDERMITE = (21, 'minecraft:endermite')
    EVOKER_FANGS = (22, 'minecraft:evoker_fangs')
    EVOKER = (23, 'minecraft:evoker')
    EXPERIENCE_ORB = (24, 'minecraft:experience_orb')
    EYE_OF_ENDER = (25, 'minecraft:eye_of_ender')
    FALLING_BLOCK = (26, 'minecraft:falling_block')
    FIREWORK_ROCKET = (27, 'minecraft:firework_rocket')
    FOX = (28, 'minecraft:fox')
    GHAST = (29, 'minecraft:ghast')
    GIANT = (30, 'minecraft:giant')
    GUARDIAN = (31, 'minecraft:guardian')
    HORSE = (32, 'minecraft:horse')
    HUSK = (33, 'minecraft:husk')
    ILLUSIONER = (34, 'minecraft:illusioner')
    ITEM = (35, 'minecraft:item')
    ITEM_FRAME = (36, 'minecraft:item_frame')
    FIREBALL = (37, 'minecraft:fireball')
    LEASH_KNOT = (38, 'minecraft:leash_knot')
    LLAMA = (39, 'minecraft:llama')
    LLAMA_SPIT = (40, 'minecraft:llama_spit')
    MAGMA_CUBE = (41, 'minecraft:magma_cube')
    MINECART = (42, 'minecraft:minecart')
    CHEST_MINECART = (43, 'minecraft:chest_minecart')
    COMMAND_BLOCK_MINECART = (44, 'minecraft:command_block_minecart')
    FURNACE_MINECART = (45, 'minecraft:furnace_minecart')
    HOPPER_MINECART = (46, 'minecraft:hopper_minecart')
    SPAWNER_MINECART = (47, 'minecraft:spawner_minecart')
    TNT_MINECART = (48, 'minecraft:tnt_minecart')
    MULE = (49, 'minecraft:mule')
    MOOSHROOM = (50, 'minecraft:mooshroom')
    OCELOT = (51, 'minecraft:ocelot')
    PAINTING = (52, 'minecraft:painting')
    PANDA = (53, 'minecraft:panda')
    PARROT = (54, 'minecraft:parrot')
    PIG = (55, 'minecraft:pig')
    PUFFERFISH = (56, 'minecraft:pufferfish')
    ZOMBIE_PIGMAN = (57, 'minecraft:zombie_pigman')
    POLAR_BEAR = (58, 'minecraft:polar_bear')
    TNT = (59, 'minecraft:tnt')
    RABBIT = (60, 'minecraft:rabbit')
    SALMON = (61, 'minecraft:salmon')
    SHEEP = (62, 'minecraft:sheep')
    SHULKER = (63, 'minecraft:shulker')
    SHULKER_BULLET = (64, 'minecraft:shulker_bullet')
    SILVERFISH = (65, 'minecraft:silverfish')
    SKELETON = (66, 'minecraft:skeleton')
    SKELETON_HORSE = (67, 'minecraft:skeleton_horse')
    SLIME = (68, 'minecraft:slime')
    SMALL_FIREBALL = (69, 'minecraft:small_fireball')
    SNOW_GOLEM = (70, 'minecraft:snow_golem')
    SNOWBALL = (71, 'minecraft:snowball')
    SPECTRAL_ARROW = (72, 'minecraft:spectral_arrow')
    SPIDER = (73, 'minecraft:spider')
    SQUID = (74, 'minecraft:squid')
    STRAY = (75, 'minecraft:stray')
    TRADER_LLAMA = (76, 'minecraft:trader_llama')
    TROPICAL_FISH = (77, 'minecraft:tropical_fish')
    TURTLE = (78, 'minecraft:turtle')
    EGG = (79, 'minecraft:egg')
    ENDER_PEARL = (80, 'minecraft:ender_pearl')
    EXPERIENCE_BOTTLE = (81, 'minecraft:experience_bottle')
    POTION = (82, 'minecraft:potion')
    TRIDENT = (83, 'minecraft:trident')
    VEX = (84, 'minecraft:vex')
    VILLAGER = (85, 'minecraft:villager')
    IRON_GOLEM = (86, 'minecraft:iron_golem')
    VINDICATOR = (87, 'minecraft:vindicator')
    PILLAGER = (88, 'minecraft:pillager')
    WANDERING_TRADER = (89, 'minecraft:wandering_trader')
    WITCH = (90, 'minecraft:witch')
    WITHER = (91, 'minecraft:wither')
    WITHER_SKELETON = (92, 'minecraft:wither_skeleton')
    WITHER_SKULL = (93, 'minecraft:wither_skull')
    WOLF = (94, 'minecraft:wolf')
    ZOMBIE = (95, 'minecraft:zombie')
    ZOMBIE_HORSE = (96, 'minecraft:zombie_horse')
    ZOMBIE_VILLAGER = (97, 'minecraft:zombie_villager')
    PHANTOM = (98, 'minecraft:phantom')
    RAVAGER = (99, 'minecraft:ravager')
    LIGHTNING_BOLT = (100, 'minecraft:lightning_bolt')
    PLAYER = (101, 'minecraft:player')
    FISHING_BOBBER = (102, 'minecraft:fishing_bobber')
