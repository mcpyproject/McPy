import enum
import logging


class ServerActionType(enum.Enum):
    """
    A list of actions used to handle the incoming network packet
    """

    def __init__(self, id, fields):
        self.id = id
        self.fields = fields

    PLAYER_JOIN = ('player_join', ['uuid', 'display_name', 'version'])
    PLAYER_LEFT = ('player_left', ['uuid'])
    CLIENT_SETTINGS = ('client_settings', ['uuid', 'entity_id', 'locale', 'view_distance', 'chat_mode', 'chat_color', 'skin_parts', 'main_hand'])


class ServerAction:

    def __init__(self, server):
        self.server = server

    def player_join(self, uuid, display_name, version):
        # Call the appropriated method to load the player
        self.server.player_manager.player_join(uuid, display_name, version)

    def player_left(self, uuid):
        # Call the appropriated method to unload the player
        self.server.player_manager.player_left(uuid)

    def client_settings(self, uuid, locale, view_distance, chat_mode, chat_color, skin_parts, main_hand):
        player = self.server.player_manager.get_player(uuid)
        if player:
            player.set_client_settings(locale, view_distance, chat_mode, chat_color, skin_parts, main_hand)
