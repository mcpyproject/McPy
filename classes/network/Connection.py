import logging
import multiprocessing
import threading

from multiprocessing.queues import Empty

from classes.utils.Utils import Version
from quarry.data import packets
from quarry.net import server
from quarry.net.protocol import ProtocolError
from twisted.internet import reactor

import classes.Server as Server

from .IncomingPacketAction import ServerAction, ServerActionType
from .PacketType import BasicNetwork, PacketType, PacketTypeInput
from .versions.v578 import v1_15_2, v1_15_2_Input
from classes.utils.Config import ConfigParser

config = ConfigParser.load_config(1)

class PlayerNetwork(server.ServerProtocol):

    def handle_loop(self):
        """
        This method will check if there is a packet to send to the player and if there is, it sends the packet
        This method is called 20 times per seconds
        """
        while True:
            try:
                item = self.TASK_QUEUE.get_nowait()
            except (KeyboardInterrupt, Empty):
                return
            if item:
                # Handle it
                packet_type = item['packet_type']
                data = item['data']
                self.make_packet_and_send(packet_type=packet_type, data=data)
            else:
                break

    def player_joined(self):
        """
        Called when a player joins the server.
        This method should call method player_joined_network of ServerFactory to completly load this player
        """
        super(PlayerNetwork, self).player_joined()
        # Load player's version
        if str(self.protocol_version) not in self.factory._protocol:
            # Version not supported
            self.close('Invalid or unsupported protocol, please use a supported version of Minecraft !')
            return
        self._protocol = self.factory._protocol[str(self.protocol_version)]
        self._protocol_input = self.factory._protocol_input[str(self.protocol_version)]
        self.version = Version.get_version(self.protocol_version)

        self.TASK_QUEUE = multiprocessing.Queue()
        self._handle_loop = self.ticker.add_loop(1, self.handle_loop)
        # Keep alive loop
        self.ticker.add_loop(20, self._update_keep_alive)
        # Notify server
        self.factory.player_joined_network(self)

    def player_left(self):
        super(PlayerNetwork, self).player_left()

        if self._handle_loop:
            self._handle_loop.stop()

        self.factory.player_left_network(self)

    def make_packet(self, packet_type: PacketType, data):
        packet_class = getattr(self._protocol, packet_type.id, None)
        if packet_class:
            return packet_class(self.buff_type, **data)
        return None

    def make_packet_and_send(self, packet_type: PacketType, data):
        packets = self.make_packet(packet_type, data)
        if packets:
            self.send_packet(packet_type.id, *packets)

    def _update_keep_alive(self):
        # Send 'keep_alive' packet
        self.make_packet_and_send(PacketType.KEEP_ALIVE, {})

    def packet_chat_message(self, buff):
        # TODO Move this logic in another place
        p_text = buff.unpack_string()
        message = "<{0}> {1}".format(self.display_name, p_text)
        logging.info(message)
        NetworkController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
                                      message=message)

    def add_packet(self, packet_type: PacketType, data):
        """
        Add a packet into the QUEUE
        The packet will be sent to the player on the next tick
        """
        self.TASK_QUEUE.put_nowait({
            'packet_type': packet_type,
            'data': data,
        })

    def on_packet(self, buff, packet_type: PacketTypeInput):
        packet_class = getattr(self._protocol_input, packet_type.id, None)
        if packet_class:
            data = packet_class(buff)
            NetworkController.execute_server(packet_type.server_action_type, uuid=self.uuid, **data)

    def packet_client_settings(self, buff):
        self.on_packet(buff, PacketTypeInput.CLIENT_SETTINGS)

    # def update_tablist(self):
    #     parsed_player_list = []
    #     for item in self._players:
    #         parse_player_list = [item[0], item[1], 0, 3, 0, True, item[1]]
    #         parsed_player_list.append(parse_player_list)
    #     self.send_packet(self.buff_type.pack(
    #         "iia",
    #         0,
    #         len(self._players),
    #         parsed_player_list
    #     ))

    # Methods overridden for compatibility ------------------------------------
    def get_packet_name(self, ident):
        protver = self.protocol_version
        if self.protocol_mode == 'status':
            protver = 578
        key = (protver, self.protocol_mode, self.recv_direction,
               ident)
        try:
            return packets.packet_names[key]
        except KeyError:
            raise ProtocolError("No name known for packet: %s" % (key,))

    def get_packet_ident(self, name):
        protver = self.protocol_version
        if self.protocol_mode == 'status':
            protver = 578
        key = (protver, self.protocol_mode, self.send_direction,
               name)
        try:
            return packets.packet_idents[key]
        except KeyError:
            raise ProtocolError("No ID known for packet: %s" % (key,))

class ServerFactory(server.ServerFactory):

    def __init__(self, host=config['ip'], port=config['port']):
        super(ServerFactory, self).__init__()
        self._host = host
        self._port = port
        self.protocol = PlayerNetwork
        self._players = self.protocol._players = {}
        self._unloaded_players = self.protocol._unloaded_players = {}
        self._protocol = {
            '578': v1_15_2()
        }
        self._protocol_input = {
            '578': v1_15_2_Input()
        }

    def pre_start_server(self):
        self.listen(self._host, self._port)

    def start_server(self):
        """
        Start the server
        THIS METHOD BLOCKS, IT SHOULD BE CALLED IN ASYNC OR IN ANOTHER THREAD
        """
        reactor.run(installSignalHandlers=False)

    def set_motd(self, motd):
        self.motd = motd

    def set_max_players(self, max_players):
        self.max_players = max_players

    def get_player(self, entity_id) -> PlayerNetwork:
        if str(entity_id) in self._players:
            return self._players[str(entity_id)]
        return None

    def get_player_protocol(self, entity_id) -> BasicNetwork:
        p = self.get_player(entity_id)
        if p and str(p.protocol_version) in self._protocol:
            return self._protocol[str(p.protocol_version)]
        return None

    def player_joined_network(self, player: PlayerNetwork):
        """
        Called when there is a new player.
        This method is called by PlayerNetwork class and should call appropriated methods in PlayerManager
        """
        # We can add player to the list
        self._unloaded_players[str(player.uuid)] = player
        NetworkController.execute_server(ServerActionType.PLAYER_JOIN, uuid=player.uuid, display_name=player.display_name, version=player.version)
        # NetworkController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
        #                               message=u"\u00a7e%s joined the game" % player.display_name)

    def player_joined_server(self, uuid, entity_id):
        """
        Called by the Server to set an entity id to a player
        """
        # Set the id of the player
        player = self._unloaded_players[str(uuid)]
        if player:
            player.entity_id = entity_id
            self._players[str(entity_id)] = player
            del self._unloaded_players[str(uuid)]

    def player_left_network(self, player: PlayerNetwork):
        """
        Called when there is a player that left.
        This method is called by PlayerNetwork class and should call appropriated methods in PlayerManager
        """
        NetworkController.execute_server(ServerActionType.PLAYER_LEFT, uuid=player.uuid)
        if str(player.entity_id) in self._players:
            del self._players[str(player.entity_id)]
        NetworkController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
                                      message=u"\u00a7e%s left the game" % player.display_name)

    def player_left_server(self, uuid=None, entity_id=-1):
        """
        Called by the Server to unload a player
        """
        if uuid:
            del self._unloaded_players[str(uuid)]
        if entity_id != -1:
            del self._players[str(entity_id)]

    def send_packet(self, packet_type: PacketType, **data):
        for entity_id in self._players:
            self.send_packet_player(entity_id, packet_type, **data)

    def send_packet_player(self, entity_id, packet_type: PacketType, **data):
        p = self.get_player(entity_id)
        if p:
            p.add_packet(packet_type, **data)


class NetworkController:
    # Outgoing data (Server => Clients)
    OUT_QUEUE = multiprocessing.Queue()
    # Incoming data (Clients => Server)
    IN_QUEUE = multiprocessing.Queue()
    # The Network Process
    networking_process: multiprocessing.Process

    @staticmethod
    def start_process(server: Server, host=config['ip'], port=config['port']):
        """
        Start the Network process
        """
        NetworkController.actions = ServerAction(server)
        NetworkController.networking_process = multiprocessing.Process(target=NetworkController.networker, args=(NetworkController.OUT_QUEUE, NetworkController.IN_QUEUE, host, port), name='NETWORK_PROCESS')
        NetworkController.networking_process.start()

    @staticmethod
    def stop_process():
        """
        Stop the Network process
        """
        if NetworkController.networking_process:
            NetworkController.networking_process.terminate()

    @staticmethod
    def networker(OUT_QUEUE, IN_QUEUE, host, port):
        """
        Here, we should be in another process.
        This process is used by the network.
        """
        NetworkController.IN_QUEUE = IN_QUEUE
        NetworkController.OUT_QUEUE = OUT_QUEUE
        server_factory = ServerFactory(host, port)
        server_factory.pre_start_server()
        server_factory.set_motd(config['motd'])
        server_factory.set_max_players(config['max_players'])

        # Let's start another thread that will start the server :D
        server_thread = threading.Thread(target=server_factory.start_server, name='NETWORK_THREAD')
        server_thread.start()
        # Enter in a loop and read outgoing network packet
        while True:
            try:
                item = NetworkController.OUT_QUEUE.get()
            except KeyboardInterrupt:
                break
            if item is None:
                break
            NetworkController._execute(server_factory, item)

    @staticmethod
    def _execute(server_factory: ServerFactory, item):
        if type(item) is not dict:
            return
        if 'action' not in item:
            return
        action = item['action']
        option = item['option'] if 'option' in item else {}
        if action == 'call_method':
            NetworkController._execute_call_method(server_factory, option)

    @staticmethod
    def _execute_call_method(server_factory: ServerFactory, option):
        # We want to call specific method
        method_name = option['name'] if 'name' in option else None
        # Check if method exists
        if method_name and hasattr(server_factory, method_name) and callable(getattr(server_factory, method_name)):
            # The method exists
            args = option['args'] if 'args' in option else {}
            # Call method
            method = getattr(server_factory, method_name)
            try:
                method(**args)
            except:
                # TODO Catch this exception
                pass

    @staticmethod
    def tick(current_tick):
        """
        Called by the server 20 times per seconds
        Handle the incoming network packets
        """
        while True:
            try:
                item = NetworkController.IN_QUEUE.get_nowait()
            except (KeyboardInterrupt, Empty):
                break
            if item is None:
                break
            action = item['action']
            data = item['data']
            method = getattr(NetworkController.actions, action.id, None)
            if method:
                # Execute the action
                method(**data)
            else:
                logging.warn('Got an unknown action: %s', action.id)

    @staticmethod
    def send_packet(packet_type: PacketType, **data):
        NetworkController.OUT_QUEUE.put_nowait({
            'action': 'call_method',
            'option': {
                'name': 'send_packet',
                'args': {
                    'packet_type': packet_type,
                    'data': data,
                },
            },
        })

    @staticmethod
    def send_packet_player(entity_id, packet_type: PacketType, data: dict):
        NetworkController.OUT_QUEUE.put_nowait({
            'action': 'call_method',
            'option': {
                'name': 'send_packet_player',
                'args': {
                    'entity_id': entity_id,
                    'packet_type': packet_type,
                    'data': data,
                },
            },
        })

    @staticmethod
    def init_player(uuid, entity_id):
        NetworkController.OUT_QUEUE.put_nowait({
            'action': 'call_method',
            'option': {
                'name': 'player_joined_server',
                'args': {
                    'uuid': uuid,
                    'entity_id': entity_id,
                },
            },
        })

    @staticmethod
    def destroy_player(uuid=None, entity_id=-1):
        NetworkController.OUT_QUEUE.put_nowait({
            'action': 'call_method',
            'option': {
                'name': 'player_left_server',
                'args': {
                    'uuid': uuid,
                    'entity_id': entity_id,
                },
            },
        })

    @staticmethod
    def execute_server(action: ServerActionType, **data):
        NetworkController.IN_QUEUE.put_nowait({
            'action': action,
            'data': data,
        })
