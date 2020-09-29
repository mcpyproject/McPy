import asyncio
import base64
import json

import networking
import struct
import zlib

from networking.protocol_578 import *
from networking.util.datatypes import VarInt


class LegacyServerPingAlert(Exception):
    pass


class Connection:
    connections = []
    
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, packet_cb):
        """
        Initialize a new Connection based on the given reader and writer pair, along with the provided callback for
        new packets.
        
        :param reader: Reader object of the new client
        :param writer: Writer object of the new client
        :param packet_cb: Callback that will be called when a new packet is received. Must be a function that takes
        one argument, the Packet that was received. (Will be one of the Packet classes provided).
        """
        self.state = "handshake"
        self.reader = reader
        self.writer = writer
        self.version = 578  # Default version of protocol we're speaking here
        self.encryption = None
        self.compression = 0
        self.remote_addr = writer.get_extra_info("peername")
        self.server_addr = (None, None)
        self.packet_cb = packet_cb
        self.connections.append(self)
    
    async def start(self):
        """Called to initialize communication with the connected client."""
        await asyncio.create_task(self._packet_listener_task())

    async def disconnect(self):
        try:
            self.writer.close()
        except Exception as e:
            # log.warning(...)
            pass
        self.connections.pop(self.connections.index(self))

    async def _async_varint_decode(self, reader: asyncio.StreamReader):
        n_bytes = 0
        number = 0
        byte = 128
        last_value = None
        while (byte & 0x80) != 0:
            if n_bytes > 4:
                raise OverflowError("VarInt too large while reading in new packet")
            n_bytes += 1
            byte = ord(await reader.read(1))
            if last_value == 0xfe and byte == 0x01 and self.state == "handshake":
                raise LegacyServerPingAlert()
            value = byte & 0x7f
            number |= value << (7 * n_bytes)
        if number > 2 ** 31 - 1:
            number -= 2 ** 32
        return number
    
    async def _packet_listener_task(self):
        while True:
            try:
                size = await self._async_varint_decode(self.reader)
                data = await self.reader.read(size)
                if data == b"":
                    raise EOFError("Unexpected EOF")
                remaining = size - len(data)
                while remaining > 0:
                    new = await self.reader.read(remaining)
                    if new == b"":
                        raise EOFError("Unexpected EOF")
                    data += await self.reader.read(remaining)
                
                if len(data) != size:
                    raise RuntimeError(f"Data size mismatch when reading in new packet: expected {size}, "
                                       f"got {len(data)}")
                if self.encryption:
                    data = self.decrypt(data)
                if self.compression:
                    data = zlib.decompress(data)
                
                # Dispatch to handlers raw packet data
                # Dispatcher will need to parse Packet ID and interpret using the relevant classes
                if self.state == "play":
                    await asyncio.create_task(self.dispatch_play_packet(data))
                elif self.state == "login":
                    await asyncio.create_task(self.dispatch_login_packet(data))
                elif self.state == "status":
                    await asyncio.create_task(self.dispatch_status_packet(data))
                elif self.state == "handshake":
                    await asyncio.create_task(self.dispatch_handshake_packet(data))
                else:
                    raise RuntimeError(f"Invalid connection state: {self.state}")
                    
            except Exception as e:
                # log error receiving packet...
                # ALSO, handle Legacy Server Ping here
                # EOFError should just close, disconnect, cleanup, etc
                pass
        # Todo: Implement listening for packets
        # When a packet is received, call the callback on it
        # This function also handles encryption and compression (future) then decodes it
        pass
        # while True:
        #     try:
    
    async def send_packet(self, packet: packets.Packet):
        """
        Send a Packet to the client. Takes in one of the Packet classes.
        
        :param packet: The Packet object to send.
        :return: True if successfully sent.
        """
        data = packet.packet_id + packet.to_bytes()
        
        if self.compression != 0:
            length = b"\x00"
            if len(data) >= self.compression:
                length = VarInt.encode(len(data))
                data = zlib.compress(data)
            data = VarInt.encode(len(length + data)) + length + data
        else:
            # No compression on protocol
            data = VarInt.encode(len(data)) + data
        
        if self.encryption is not None:
            data = self.encrypt(data)
        
        self.writer.write(data)
        await self.writer.drain()
    
    def decrypt(self, data):
        return data
    
    def encrypt(self, data):
        return data
    
    async def handle_legacy_ping(self):
        # Packet format from https://wiki.vg/Server_List_Ping#1.6
        fixed_content = await self.reader.read(25)  # Read the fixed portion of the Legacy Server Ping packet
        if fixed_content != b"\xfa\0\x0b\0M\0C\0|\0P\0i\0n\0g\0H\0o\0s\0t":
            pass  # idk man raise an error or something? it should always be this but idk
        length, = struct.unpack(">h", await self.reader.read(2))
        data = self.reader.read(length)  # rest of packet (hostname, port, etc)
        version, hostname_len = struct.unpack(">bh", data[:3])
        hostname = data[3:3+(hostname_len*2)]
        port, = struct.unpack(">i", data[-4:])  # Encoding the port as an int is an absolute galaxy brain idea
        
        # todo: respond to the client lmao
        
        pass
    
    async def dispatch_handshake_packet(self, data):
        pid, data = VarInt.decode(data)
        packet = handshake_packet_lookup[pid](data)
        if isinstance(packet, packets.Handshake):
            self.version = packet.protocol_version
            self.server_addr = (packet.server_address, packet.server_port)
            if packet.next_state == 1:
                self.state = "status"
            elif packet.next_state == 2:
                self.state = "login"
            else:
                raise RuntimeError(f"invalid Next State received?: {packet.next_state}")
            
    async def dispatch_status_packet(self, data):
        packet_id, data = VarInt.decode(data)
        try:
            packet = status_packet_lookup.get("packet_id", None)(data)
        except TypeError:
            # NoneType is not callable
            raise RuntimeError("Packet type not found in packet class lookup")
        if isinstance(packet, packets.Request):
            players = []  # Todo: Get list of players; this should be some server thing or a Connections thing
            response = {
                "version": {
                    "name": game_version,
                    "protocol": version
                },
                "players": {
                    "max": 250,  # Todo: max players should be a property of a ServerSettings object
                    "online": len(Connection.connections),
                    "sample": [{"name": x.name, "id": x.id} for x in players]
                    # ID should have dashed UUID
                },
                "description": {
                    "text": "Server MOTD"  # This field is a Chat component
                }
            }
            if None is not None:
                response["favicon"] = "data:image/png;base64," + base64.b64encode("Image Object Here").decode()
                # todo: image object should be a property of a ServerSettings object
                #  Such object should also pre-b64encode the image for us
            await self.send_packet(packets.Response(json.dumps(response)))
        
        if isinstance(packet, packets.Ping):
            await self.send_packet(packets.Pong(packet.payload))
            await self.disconnect()

    async def dispatch_login_packet(self, data):
        pass

    async def dispatch_play_packet(self, data):
        # Should call a registered handler, with a decorator to register new handlers for specific packets.
        pass

# Todo: Need to have packet listeners before and after encryption, compression, and raw socket, on both send and
#  receive side in order to allow protocol inspection
