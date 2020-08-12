# Temporary class

from quarry.net import server

# The next two classes are from https://quarry.readthedocs.io
class ChatRoomProtocol(server.ServerProtocol):
    request_item_queue = REQUEST_QUEUE

    def player_joined(self):
        # Call super. This switches us to "play" mode, marks the player as
        #   in-game, and does some logging.
        server.ServerProtocol.player_joined(self)

        # Send "Join Game" packet
        self.send_packet("join_game",
                         self.buff_type.pack("iBqiB",
                                             0,  # entity id
                                             3,  # game mode
                                             0,  # dimension
                                             0,  # hashed seed
                                             0),  # max players
                         self.buff_type.pack_string("flat"),  # level type
                         self.buff_type.pack_varint(1),  # view distance
                         self.buff_type.pack("??",
                                             False,  # reduced debug info
                                             True))  # show respawn screen

        # Send "Player Position and Look" packet
        self.send_packet("player_position_and_look",
                         self.buff_type.pack("dddff?",
                                             0,  # x
                                             255,  # y
                                             0,  # z
                                             0,  # yaw
                                             0,  # pitch
                                             0b00000),  # flags
                         self.buff_type.pack_varint(0))  # teleport id

        # Start sending "Keep Alive" packets
        self.ticker.add_loop(20, self.update_keep_alive)
        self.ticker.add_loop(100, self.send_day_time_update)

        players.append([self.uuid, self.display_name])

        self.update_tablist()

        # Announce player joined
        self.factory.send_chat(u"\u00a7e%s has joined." % self.display_name)

    def player_left(self):
        server.ServerProtocol.player_left(self)

        players.remove([self.uuid, self.display_name])
        self.update_tablist()
        # Announce player left
        self.factory.send_chat(u"\u00a7e%s has left." % self.display_name)

    def update_keep_alive(self):
        # Send a "Keep Alive" packet

        # 1.7.x
        if self.protocol_version <= 338:
            payload = self.buff_type.pack_varint(0)

        # 1.12.2
        else:
            payload = self.buff_type.pack('Q', 0)

        self.send_packet("keep_alive", payload)

    def packet_chat_message(self, buff):
        # When we receive a chat message from the player, ask the factory
        # to relay it to all connected players
        p_text = buff.unpack_string()
        chat_msg = "<{0}> {1}".format(self.display_name, p_text)
        self.factory.send_chat(chat_msg)
        logging.info(chat_msg)

    def send_day_time_update(self):
        self.send_packet(self.buff_type.pack(
            "ii",  # Field one will be a int (or any of Java's integer representations), and so will field 2
            totalTime,  # Field one is the total overall game time
            dayTime  # Field two is the current time of day
        ))

    def update_tablist(self):
        parsedPlayerList = []
        for item in players:
            parsePlayerList = [item[0], item[1], 0, 3, 0, True, item[1]]
            parsedPlayerList.append(parsePlayerList)
        self.send_packet(self.buff_type.pack(
            "iia",
            0,
            len(players),
            parsedPlayerList
        ))


class ChatRoomFactory(server.ServerFactory):
    protocol = ChatRoomProtocol
    motd = "Chat Room Server"  # Later customizable

    def send_chat(self, message):
        for player in self.players:
            player.send_packet("chat_message", player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0))