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

    def translate_alternate_color(alt_color, text):
        list_text = list(text)
        for i in range(len(list_text) - 1):
            if text[i] == alt_color and '0123456789abcdefklmnorABCDEFKLMNOR'.find(text[i + 1]) > -1:
                list_text[i] = ChatColor.key()
                list_text[i + 1] = text[i + 1].lower()
        return ''.join(list_text)

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

    NETHER = -1
    OVERWORLD = 0
    THE_END = 1


class Effect(Enum):
    """ Effects, ordered by name """

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    ABSORPTION = ('absorption')
    BAD_OMEN = ('bad_omen')
    BLINDNESS = ('blindness')
    CONDUIT_POWER = ('conduit_power')
    DOLPHINE_GRACE = ('dolphins_grace')
    FIRE_RESISTANCE = ('fire_resistance')
    GLOWING = ('glowing')
    HASTE = ('haste')
    HEALTH_BOOST = ('health_boost')
    HERO_OF_THE_VILLAGE = ('hero_of_the_village')
    HUNGER = ('hunger')
    INSTANT_DAMAGE = ('instant_damage')
    INSTANT_HEALTH = ('instant_health')
    INVISIBILITY = ('invisibility')
    JUMP_BOOST = ('jump_boost')
    LEVITATION = ('levitation')
    LUCK = ('luck')
    MINING_FATIGUE = ('mining_fatigue')
    NAUSEA = ('nausea')
    NIGHT_VISION = ('night_vision')
    REGENERATION = ('regeneration')
    RESISTANCE = ('resistance')
    POISON = ('poison')
    SATURATION = ('saturation')
    SLOW_FALLING = ('slow_falling')
    SLOWNESS = ('slowness')
    SPEED = ('speed')
    STRENGTH = ('strength')
    UNLUCk = ('unluck')
    WATER_BREATHING = ('water_breathing')
    WEAKNESS = ('weakness')
    WITHER = ('wither')


class Enchantment(Enum):

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    PROTECTION = ('protection')
    FIRE_PROTECTION = ('fire_protection')
    FEATHER_FALLING = ('feather_falling')
    BLAST_PROTECTION = ('blast_protection')
    PROJECTILE_PROTECTION = ('projectile_protection')
    RESPIRATION = ('respiration')
    AQUA_AFFINITY = ('aqua_affinity')
    THORNS = ('thorns')
    DEPTH_STRIDER = ('depth_strider')
    FROST_WALKER = ('frost_walker')
    BINDING_CURSE = ('binding_curse')
    SHARPNESS = ('sharpness')
    SMITE = ('smite')
    BANE_OF_ARTHROPODS = ('bane_of_arthropods')
    KNOCKBACK = ('knockback')
    FIRE_ASPECT = ('fire_aspect')
    LOOTING = ('looting')
    SWEEPING = ('sweeping')
    EFFICIENCY = ('efficiency')
    SILK_TOUCH = ('silk_touch')
    UNBREAKING = ('unbreaking')
    FORTUNE = ('fortune')
    POWER = ('power')
    PUNCH = ('punch')
    FLAME = ('flame')
    INFINITY = ('infinity')
    LUCK_OF_THE_SEA = ('luck_of_the_sea')
    LURE = ('lure')
    LOYALTY = ('loyalty')
    IMPALING = ('impaling')
    RIPTIDE = ('riptide')
    CHANNELING = ('channeling')
    MULTISHOT = ('multishot')
    QUICK_CHARGE = ('quick_charge')
    PIERCING = ('piercing')
    MENDING = ('mending')
    VANISHING_CURSE = ('vanishing_curse')


class Entity(Enum):
    """ Entities, ordered by name """

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    AREA_EFFECT_CLOUD = ('area_effect_cloud')
    ARMOR_STAND = ('armor_stand')
    ARROW = ('arrow')
    BAT = ('bat')
    BEE = ('bee')
    BLAZE = ('blaze')
    BOAT = ('boat')
    CAT = ('cat')
    CAVE_SPIDER = ('cave_spider')
    CHICKEN = ('chicken')
    COD = ('cod')
    COW = ('cow')
    CREEPER = ('creeper')
    DOLPHIN = ('dolphin')
    DONKEY = ('donkey')
    DRAGON_FIREBALL = ('dragon_fireball')
    DROWNED = ('drowned')
    EGG = ('egg')
    ELDER_GUARDIAN = ('elder_guardian')
    END_CRYSTAL = ('end_crystal')
    ENDER_DRAGON = ('ender_dragon')
    ENDER_PEARL = ('ender_pearl')
    ENDERMAN = ('enderman')
    ENDERMITE = ('endermite')
    EVOKER = ('evoker')
    EVOKER_FANGS = ('evoker_fangs')
    EXPERIENCE_BOTTLE = ('experience_bottle')
    EXPERIENCE_ORB = ('experience_orb')
    EYE_OF_ENDER = ('eye_of_ender')
    FALLING_BLOCK = ('falling_block')
    FISHING_HOOK = ('fishing_bobber')
    FIREBALL = ('fireball')
    FIREWORK_ROCKET = ('firework_rocket')
    FOX = ('fox')
    GHAST = ('ghast')
    GIANT = ('giant')
    GUARDIAN = ('guardian')
    HOGLIN = ('hoglin')
    HORSE = ('horse')
    HUSK = ('husk')
    ILLUSIONER = ('illusioner')
    IRON_GOLEM = ('iron_golem')
    ITEM = ('item')
    ITEM_FRAME = ('item_frame')
    LEASH_KNOT = ('leash_knot')
    LIGHTNING_BOLT = ('lightning_bolt')
    LLAMA = ('llama')
    LLAMA_SPIT = ('llama_spit')
    MAGMA_CUBE = ('magma_cube')
    MINECART = ('minecart')
    MINECART_CHEST = ('chest_minecart')
    MINECART_COMMAND_BLOCK = ('commandblock_minecart')
    MINECART_FURNACE = ('furnace_minecart')
    MINECART_HOPPER = ('hopper_minecart')
    MINECART_SPAWNER = ('spawner_minecart')
    MINECART_TNT = ('tnt_minecart')
    MULE = ('mule')
    MUSHROOM = ('mooshroom')
    OCELOT = ('ocelot')
    PAINTING = ('painting')
    PANDA = ('panda')
    PARROT = ('parrot')
    PIG = ('pig')
    PIGLIN = ('piglin')
    PIGLIN_BRUTE = ('piglin_brute')
    PILLAGER = ('pillager')
    PLAYER = ('player')
    PHANTOM = ('phantom')
    POLAR_BEAR = ('polar_bear')
    POTION = ('potion')
    PUFFERFISH = ('pufferfish')
    RABBIT = ('rabbit')
    RAVAGER = ('ravager')
    SALMON = ('salmon')
    SHEEP = ('sheep')
    SHULKER = ('shulker')
    SHULKER_BULLET = ('shulker_bullet')
    SILVERFISH = ('silverfish')
    SKELETON = ('skeleton')
    SKELETON_HORSE = ('skeleton_horse')
    SLIME = ('slime')
    SMALL_FIREBALL = ('small_fireball')
    SNOW_GOLEM = ('snow_golem')
    SNOWBALL = ('snowball')
    SPECTRAL_ARROW = ('spectral_arrow')
    SPIDER = ('spider')
    SQUID = ('squid')
    STRAY = ('stray')
    STRIDER = ('strider')
    TNT = ('tnt')
    TRIDENT = ('trident')
    TRADER_LLAMA = ('trader_llama')
    TROPICAL_FISH = ('tropical_fish')
    TURTLE = ('turtle')
    VEX = ('vex')
    VILLAGER = ('villager')
    VINDICATOR = ('vindicator')
    WANDERING_TRADER = ('wandering_trader')
    WITCH = ('witch')
    WITHER = ('wither')
    WITHER_SKELETON = ('wither_skeleton')
    WITHER_SKULL = ('wither_skull')
    WOLF = ('wolf')
    ZOGLIN = ('zoglin')
    ZOMBIE = ('zombie')
    ZOMBIE_HORSE = ('zombie_horse')
    ZOMBIE_VILLAGER = ('zombie_villager')
    ZOMBIE_PIGMAN = ('zombie_pigman')
