import enum

from .IncomingPacketAction import ServerActionType


class PacketType(enum.Enum):
    """
    Server => Client
    """

    def __init__(self, id, fields):
        self.id = id
        self.fields = fields

    JOIN_GAME = ('join_game', ['entity_id', 'uuid', 'gamemode', 'dimension', 'hashed_seed', 'max_player', 'level_type', 'view_distance', 'reduced_debug_info', 'show_respawn_screen'])
    PLUGIN_MESSAGE = ('plugin_message', ['channel', 'data'])
    SERVER_DIFFICULTY = ('server_difficulty', ['difficulty', 'difficulty_locked'])
    PLAYER_ABILITIES = ('player_abilities', ['flag', 'default_speed', 'default_fov'])
    PLAYER_POSITION_AND_LOOK = ('player_position_and_look', ['x', 'y', 'z', 'yaw', 'pitch', 'flags', 'entity_id'])
    KEEP_ALIVE = ('keep_alive', [])
    TIME_UPDATE = ('time_update', ['game_time', 'day_time'])
    CHAT_MESSAGE = ('chat_message', ['message'])


class PacketTypeInput(enum.Enum):
    """
    Client => Server
    """

    def __init__(self, id, server_action_type: ServerActionType, fields):
        self.id = id
        self.server_action_type = server_action_type
        self.fields = fields

    CLIENT_SETTINGS = ('client_settings', ServerActionType.CLIENT_SETTINGS, ['locale', 'view_distance', 'chat_mode', 'chat_color', 'skin_parts', 'main_hand'])


class BasicNetwork:
    """
    Abstract class to transform data into readable packets
    """

    @staticmethod
    def join_game(buff_type, entity_id=0, gamemode=0, dimension=0, hashed_seed=0, max_player=1, level_type='flat', view_distance=8, reduced_debug_info=False, show_respawn_screen=True):
        raise NotImplementedError()

    @staticmethod
    def plugin_message(buff_type, channel=None, data=None):
        raise NotImplementedError()

    @staticmethod
    def server_difficulty(buff_type, difficulty=0, difficulty_locked=True):
        raise NotImplementedError()

    @staticmethod
    def player_abilities(buff_type, flag=0, default_speed=0.05, default_fov=0.1):
        raise NotImplementedError()

    @staticmethod
    def player_position_and_look(buff_type, x=0, y=0, z=0, yaw=0.0, pitch=0.0, flags=0, entity_id=0):
        raise NotImplementedError()

    @staticmethod
    def keep_alive(buff_type):
        raise NotImplementedError()

    @staticmethod
    def time_update(buff_type, game_time=0, day_time=0):
        raise NotImplementedError()

    @staticmethod
    def chat_message(buff_type, message=None):
        raise NotImplementedError()


class BasicNetworkInput:
    """
    Abstract class to transform packets into data
    """

    @staticmethod
    def client_settings(buff_type):
        raise NotImplementedError()
