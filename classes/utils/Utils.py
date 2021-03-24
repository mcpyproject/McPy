import re

from enum import Enum, IntEnum


class Version(Enum):

    def __init__(self, major, minor, version, protocol, data_id):
        self.major = major
        self.minor = minor
        self.version = version
        self.protocol = protocol
        self.data_id = data_id
        self.all = (major, minor, version)

    def is_same_major(self, other_version):
        return self.major == other_version.major

    @staticmethod
    def get_version(protocol):
        for v in Version:
            if v.protocol == protocol:
                return v
        return None

    @staticmethod
    def get_version_data_file(data_id):
        for v in Version:
            if v.data_id == data_id:
                return v
        return None

    def to_string(self):
        return '{}.{}.{}'.format(self.major, self.minor, self.version)

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

    v1_12_0 = (1, 12, 0, 335, '1.12')
    v1_12_1 = (1, 12, 1, 338, '1.12.1')
    v1_12_2 = (1, 12, 2, 340, '1.12.2')
    v1_13_0 = (1, 13, 0, 393, '1.13')
    v1_13_1 = (1, 13, 1, 401, '1.13.1')
    v1_13_2 = (1, 13, 2, 404, '1.13.2')
    v1_14_0 = (1, 14, 0, 477, '1.14')
    v1_14_1 = (1, 14, 1, 480, '1.14.1')
    v1_14_2 = (1, 14, 2, 485, '1.14.2')
    v1_14_3 = (1, 14, 3, 490, '1.14.3')
    v1_14_4 = (1, 14, 4, 498, '1.14.4')
    v1_15_0 = (1, 15, 0, 573, '1.15')
    v1_15_1 = (1, 15, 1, 575, '1.15.1')
    v1_15_2 = (1, 15, 2, 578, '1.15.2')
    v1_16_0 = (1, 16, 0, 735, '1.16')
    v1_16_1 = (1, 16, 1, 736, '1.16.1')
    v1_16_2 = (1, 16, 2, 751, '1.16.2')
    v1_16_3 = (1, 16, 3, 753, '1.16.3')
    v1_16_4 = (1, 16, 4, 754, '1.16.4')
    v1_16_5 = (1, 16, 5, 754, '1.16.5')


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

    @staticmethod
    def key():
        return '§'

    @staticmethod
    def strip_color(input):
        return regex_color.sub('', input)

    @staticmethod
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


class Particle(Enum):
    """ Particles, ordered by name """

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    AMBIENT_ENTITY_EFFECT = ('ambient_entity_effect')
    ANGRY_VILLAGER = ('angry_villager')
    BARRIER = ('barrier')
    BLOCK = ('block')
    BUBBLE = ('bubble')
    CLOUD = ('cloud')
    CRIT = ('crit')
    DAMAGE_INDICATOR = ('damage_indicator')
    DRAGON_BREATH = ('dragon_breath')
    DRIPPING_LAVA = ('dripping_lava')
    DRIPPING_WATER = ('dripping_water')
    DUST = ('dust')
    FALLING_LAVA = ('falling_lava')
    FALLING_WATER = ('falling_water')
    LANDING_LAVA = ('landing_lava')
    EFFECT = ('effect')
    ELDER_GUARDIAN = ('elder_guardian')
    ENCHANTED_HIT = ('enchanted_hit')
    ENCHANT = ('enchant')
    END_ROD = ('end_rod')
    ENTITY_EFFECT = ('entity_effect')
    EXPLOSION_EMITTER = ('explosion_emitter')
    EXPLOSION = ('explosion')
    FALLING_DUST = ('falling_dust')
    FIREWORK = ('firework')
    FISHING = ('fishing')
    FLAME = ('flame')
    SOUL_FIRE_FLAME = ('soul_fire_flame')
    SOUL = ('soul')
    FLASH = ('flash')
    HAPPY_VILLAGER = ('happy_villager')
    COMPOSTER = ('composter')
    HEART = ('heart')
    INSTANT_EFFECT = ('instant_effect')
    ITEM = ('item')
    ITEM_SLIME = ('item_slime')
    ITEM_SNOWBALL = ('item_snowball')
    LARGE_SMOKE = ('large_smoke')
    LAVA = ('lava')
    MYCELIUM = ('mycelium')
    NOTE = ('note')
    POOF = ('poof')
    PORTAL = ('portal')
    RAIN = ('rain')
    SMOKE = ('smoke')
    SNEEZE = ('sneeze')
    SPIT = ('spit')
    SQUID_INK = ('squid_ink')
    SWEEP_ATTACK = ('sweep_attack')
    TOTEM_OF_UNDYING = ('totem_of_undying')
    UNDERWATER = ('underwater')
    SPLASH = ('splash')
    WITCH = ('witch')
    BUBBLE_POP = ('bubble_pop')
    CURRENT_DOWN = ('current_down')
    BUBBLE_COLUMN_UP = ('bubble_column_up')
    NAUTILUS = ('nautilus')
    DOLPHIN = ('dolphin')
    CAMPFIRE_COSY_SMOKE = ('campfire_cosy_smoke')
    CAMPFIRE_SIGNAL_SMOKE = ('campfire_signal_smoke')
    DRIPPING_HONEY = ('dripping_honey')
    FALLING_HONEY = ('falling_honey')
    LANDING_HONEY = ('landing_honey')
    FALLING_NECTAR = ('falling_nectar')
    ASH = ('ash')
    CRIMSON_SPORE = ('crimson_spore')
    WARPED_SPORE = ('warped_spore')
    DRIPPING_OBSIDIAN_TEAR = ('dripping_obsidian_tear')
    FALLING_OBSIDIAN_TEAR = ('falling_obsidian_tear')
    LANDING_OBSIDIAN_TEAR = ('landing_obsidian_tear')
    REVERSE_PORTAL = ('reverse_portal')
    WHITE_ASH = ('white_ash')
