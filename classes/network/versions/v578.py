from ..PacketType import BasicNetwork, BasicNetworkInput


class v1_15_2(BasicNetwork):

    @staticmethod
    def join_game(buff_type, entity_id=0, gamemode=0, dimension=0, hashed_seed=0, max_player=1, level_type='flat', view_distance=8, reduced_debug_info=True, show_respawn_screen=True):
        return [
            buff_type.pack("iBiqB", entity_id, gamemode, dimension, hashed_seed, max_player),
            buff_type.pack_string(level_type),
            buff_type.pack_varint(view_distance),
            buff_type.pack('??', reduced_debug_info, show_respawn_screen)
        ]

    @staticmethod
    def plugin_message(buff_type, channel=None, data=None):
        return [
            buff_type.pack_string(channel),
            buff_type.pack_string(data)
        ]

    @staticmethod
    def server_difficulty(buff_type, difficulty=0, difficulty_locked=True):
        return [
            buff_type.pack('B?', difficulty, difficulty_locked)
        ]

    @staticmethod
    def player_abilities(buff_type, flag=0, default_speed=0.05, default_fov=0.1):
        return [
            buff_type.pack('bff', flag, default_speed, default_fov)
        ]

    @staticmethod
    def player_position_and_look(buff_type, x=0, y=0, z=0, yaw=0.0, pitch=0.0, flags=0, entity_id=0):
        return [
            buff_type.pack('dddff?', x, y, z, yaw, pitch, flags),
            buff_type.pack_varint(entity_id)
        ]

    @staticmethod
    def keep_alive(buff_type):
        return [
            buff_type.pack('Q', 0)
        ]

    @staticmethod
    def time_update(buff_type, game_time=0, day_time=0):
        return [
            buff_type.pack('QQ', game_time, day_time)
        ]

    @staticmethod
    def chat_message(buff_type, message=None):
        return [
            buff_type.pack_chat(message) + buff_type.pack('B', 0)
        ]


class v1_15_2_Input(BasicNetworkInput):

    @staticmethod
    def client_settings(buff_type):
        # ['locale', 'view_distance', 'chat_mode', 'chat_color', 'skin_parts', 'main_hand']
        locale = buff_type.unpack_string()
        view_distance = buff_type.unpack('b')
        chat_mode = buff_type.unpack_varint()
        chat_color = buff_type.unpack('?')
        skin_parts = buff_type.unpack('B')
        main_hand = buff_type.unpack_varint()
        return {
            'locale': locale,
            'view_distance': view_distance,
            'chat_mode': chat_mode,
            'chat_color': chat_color,
            'skin_parts': skin_parts,
            'main_hand': main_hand,
        }
