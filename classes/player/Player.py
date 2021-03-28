import logging
import json

import classes.Server as Server

from classes.entity.Entity import Entity
from classes.network.Connection import NetworkController
from classes.network.PacketType import PacketType
from classes.utils.Vector import Vector3D
from classes.utils.Utils import Version

class Player(Entity):

    def __init__(self, entity_id, player_location: Vector3D, world, uuid, display_name, version: Version, x_rot=0, y_rot=0):
        super(Player, self).__init__(entity_id, player_location, world, x_rot=x_rot, y_rot=y_rot)
        self.uuid = uuid
        self.display_name = display_name
        self.version = version
        self.locale = 'en_us'
        self.view_distance = 8
        self.chat_mode = 0
        self.chat_color = True
        self.skin_parts = 127
        self.main_hand = 1

    def set_client_settings(self, locale, view_distance, chat_mode, chat_color, skin_parts, main_hand):
        self.locale = locale
        self.view_distance = view_distance
        self.chat_mode = chat_mode
        self.chat_color = chat_color
        self.skin_parts = skin_parts
        self.main_hand = main_hand


class PlayerManager():

    def __init__(self, server: Server):
        self.server = server
        self.players = {}

    def player_join(self, uuid, display_name, version: Version):
        player = self.server.entity_manager.make_entity(Player, Vector3D(0, 72, 0), 'world', uuid=uuid, display_name=display_name, version=version)
        self.players[str(player.uuid)] = player
        logging.info('New player: uuid = %s, name = %s, version = %s', uuid, display_name, version)
        NetworkController.init_player(uuid, player.entity_id)
        # Send general packets
        self.send_join_packets(player)

    def player_left(self, uuid):
        player = self.players[str(uuid)]
        if not player:
            return
        # Destroy entity
        self.server.entity_manager.destroy_entity(player.entity_id)
        del self.players[str(uuid)]
        logging.info('Lost player %s (%s)', uuid, player.display_name)
        NetworkController.destroy_player(uuid=uuid, entity_id=player.entity_id)

    def get_player(self, uuid):
        return self.players[str(uuid)]

    def get_player_from_name(self, player_name):
        for p in self.players.values():
            if p.display_name == player_name:
                return p
        return None

    def get_players(self):
        return self.players.items()

    def send_join_packets(self, player: Player):
        # 'join_game'
        NetworkController.send_packet_player(player.entity_id, PacketType.JOIN_GAME, {
            'gamemode': 3,
            'dimension': 0,
            'hashed_seed': 0,
            'max_player': 100,
            'level_type': 'flat',
            'view_distance': 8,
            'reduced_debug_info': False,
            'show_respawn_screen': True,

        })
        # 'brand'
        NetworkController.send_packet_player(player.entity_id, PacketType.PLUGIN_MESSAGE, {
            'channel': 'minecraft:brand',
            'data': 'McPy',
        })
        # 'difficulty'
        NetworkController.send_packet_player(player.entity_id, PacketType.SERVER_DIFFICULTY, {
            'difficulty': 0,
            'difficulty_locked': True,
        })
        # 'player_ability'
        NetworkController.send_packet_player(player.entity_id, PacketType.PLAYER_ABILITIES, {
            'flag': 0,
            'default_speed': 0.05,
            'default_fov': 0.1,
        })
        # 'player_position_and_look'
        NetworkController.send_packet_player(player.entity_id, PacketType.PLAYER_POSITION_AND_LOOK, {
            'x': player.entity_location.x,
            'y': player.entity_location.y,
            'z': player.entity_location.z,
            'yaw': 0.0,
            'pitch': 0.0,
            'flags': 0,
            'entity_id': player.entity_id,
        })
