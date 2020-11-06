import multiprocessing

from multiprocessing.queues import Empty

from classes.utils.Utils import Version
from quarry.net import server
from threading import Thread
from twisted.internet import reactor

from .PacketType import BasicNetwork, PacketType
from .versions.v578 import v1_15_2


# TODO Change that
entity_id = 1
QUEUE_SIZE = 100000


class PlayerNetwork(server.ServerProtocol):

    def handle_loop(self):
        """
        This method will check if there is a packet to send to the player and if there is, it sends the packet\n
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
        super(PlayerNetwork, self).player_joined()

        if str(self.protocol_version) not in self.factory._protocol:
            # Version not supported
            self.close('Invalid protocol or not supported, please use a supported version of Minecraft !')
            return
        self._protocol = self.factory._protocol[str(self.protocol_version)]
        self.version = Version.get_version(self.protocol_version)

        self.TASK_QUEUE = multiprocessing.Queue(QUEUE_SIZE)
        self._handle_loop = self.ticker.add_loop(1, self.handle_loop)

        # TODO Generate it
        global entity_id
        self.entity_id = entity_id
        entity_id = entity_id + 1

        # TODO Move it to another place (the next 5 make_packet_and_send should be sent by the server and not be hardcoded here !!!!)
        # Send 'join_game' packet
        self.make_packet_and_send(PacketType.JOIN_GAME, {
            'entity_id': self.entity_id,
            'gamemode': 3,
            'dimension': 0,
            'hashed_seed': 0,
            'max_player': 100,
            'level_type': 'flat',
            'view_distance': 8,
            'reduced_debug_info': False,
            'show_respawn_screen': True,
        })
        # Send 'brand' packet
        self.make_packet_and_send(PacketType.PLUGIN_MESSAGE, {
            'channel': 'minecraft:brand',
            'data': 'McPy/0.0.1-alpha',  # TODO Edit that
        })
        # Send 'difficulty' packet
        self.make_packet_and_send(PacketType.SERVER_DIFFICULTY, {
            'difficulty': 0,
            'difficulty_locked': True,
        })
        # Send 'player_ability' packet
        self.make_packet_and_send(PacketType.PLAYER_ABILITIES, {
            'flag': 0,
            'default_speed': 0.05,
            'default_fov': 0.1,
        })
        # Send 'player_position_and_look' packet
        self.make_packet_and_send(PacketType.PLAYER_POSITION_AND_LOOK, {
            'x': 0,
            'y': 0,
            'z': 0,
            'yaw': 0.0,
            'pitch': 0.0,
            'flags': 0,
            'entity_id': self.entity_id,
        })
        # Start looper
        self.ticker.add_loop(20, self._update_keep_alive)
        # Notify server
        self.factory._player_joined(self)

    def player_left(self):
        super(PlayerNetwork, self).player_left()

        self.factory._player_left(self)
        if self._handle_loop:
            self._handle_loop.stop()

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
        ServerThreadController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
                                           message="<{0}> {1}".format(self.display_name, p_text))

    def add_packet(self, packet_type: PacketType, data):
        """
        Add a packet into the QUEUE\n
        The packet will be sent to the player on the next tick
        """
        self.TASK_QUEUE.put_nowait({
            'packet_type': packet_type,
            'data': data,
        })

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


class ServerFactory(server.ServerFactory):

    def __init__(self, host='localhost', port=25565):
        super(ServerFactory, self).__init__()
        self._host = host
        self._port = port
        self.protocol = PlayerNetwork
        self._players = self.protocol._players = {}
        self._protocol = {
            '578': v1_15_2()
        }

    def pre_start_server(self):
        self.listen(self._host, self._port)

    def start_server(self):
        """
        Start the server\n
        THIS METHOD BLOCKS, IT SHOULD BE CALLED IN ASYNC OR IN ANOTHER THREAD
        """
        reactor.run(installSignalHandlers=False)

    def motd(self, motd):
        self.motd = motd

    def get_player(self, entity_id) -> PlayerNetwork:
        if str(entity_id) in self._players:
            return self._players[str(entity_id)]
        return None

    def get_player_protocol(self, entity_id) -> BasicNetwork:
        p = self.get_player(entity_id)
        if p and str(p.protocol_version) in self._protocol:
            return self._protocol[str(p.protocol_version)]
        return None

    def _player_joined(self, player: PlayerNetwork):
        # TODO Call a method in the main core
        # We can add player to the list
        self._players[str(player.entity_id)] = player
        ServerThreadController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
                                           message=u"\u00a7e%s joined the game" % player.display_name)

    def _player_left(self, player):
        # TODO Call a method in the main core
        # In any cases, we MUST remove the player from the list
        if str(player.entity_id) in self._players:
            del self._players[str(player.entity_id)]
        ServerThreadController.send_packet(packet_type=PacketType.CHAT_MESSAGE,
                                           message=u"\u00a7e%s left the game" % player.display_name)

    def send_packet(self, packet_type: PacketType, **data):
        for entity_id in self._players:
            self.send_packet_player(entity_id, packet_type, **data)

    def send_packet_player(self, entity_id, packet_type: PacketType, **data):
        p = self.get_player(entity_id)
        if p:
            p.add_packet(packet_type, **data)
            # p.make_packet_and_send(packet_type, **data)


class ServerThreadController:
    # Incoming data to perform by the Network Process
    TASK_QUEUE: multiprocessing.Queue
    # The Network Process
    networking_process: multiprocessing.Process

    def __init__(self, host='localhost', port=25565):
        self.host = host
        self.port = port
        ServerThreadController.TASK_QUEUE = multiprocessing.Queue(QUEUE_SIZE)

    def start_process(self):
        """
        Start the Network process
        """
        self.networking_process = multiprocessing.Process(target=ServerThreadController.networker, args=(ServerThreadController.TASK_QUEUE, self.host, self.port))
        self.networking_process.start()

    def stop_process(self):
        """
        Stop the Network process
        """
        if self.networking_process:
            self.networking_process.terminate()

    @staticmethod
    def networker(TASK_QUEUE, host, port):
        ServerThreadController.TASK_QUEUE = TASK_QUEUE
        server_factory = ServerFactory(host, port)
        server_factory.pre_start_server()

        # Start the other process that will start the server
        server_thread = Thread(target=server_factory.start_server)
        server_thread.start()
        # Enter in a loop and read incoming network packet
        while True:
            try:
                item = ServerThreadController.TASK_QUEUE.get()
            except KeyboardInterrupt:
                break
            if item is None:
                break
            ServerThreadController._execute(server_factory, item)

    @staticmethod
    def _execute(server_factory: ServerFactory, item):
        if type(item) is not dict:
            return
        if 'action' not in item:
            return
        action = item['action']
        option = item['option'] if 'option' in item else {}
        if action == 'call_method':
            ServerThreadController._execute_call_method(server_factory, option)

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
    def send_packet(packet_type: PacketType, **data):
        ServerThreadController.TASK_QUEUE.put_nowait({
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
    def send_packet_player(entity_id, packet_type: PacketType, **data):
        ServerThreadController.TASK_QUEUE.put_nowait({
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
