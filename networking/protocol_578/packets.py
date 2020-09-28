import enum
import string
import struct

from dataclasses import dataclass, fields, field, Field, InitVar
from networking.protocol_578 import packet_id_lookup
from networking.util.vartypes import VarInt
from typing import List, Tuple


# TODO: move to datatypes module? (maybe just a renamed vartypes)
def decode_string(packet):
    """
    Decode a String from a packet and return the string and the remainder of the packet.
    
    :param packet: Packet to parse the next String from.
    :return: The String that was read, along with the rest of the packet.
    """
    length, packet = VarInt.decode(packet)
    s = packet[:length]
    return s, packet[length:]


def encode_string(s):
    """
    Encode a String to corresponding bytes[] object.
    
    :param s: String to encode.
    :return: Encoded String.
    """
    return VarInt.encode(len(s)) + s.encode("utf-8")


class Packet:
    @property
    def packet_id(self) -> str:
        s = self.__class__.__name__
        for char in string.ascii_uppercase:
            s = s.replace(char, f"_{char}")
        return packet_id_lookup[s.replace("_", "", 1)]  # 2nd .replace() in there to rid leading _

    def to_bytes(self):
        raise NotImplemented


# There are no clientbound packets in the Handshaking state, since the protocol
# immediately switches to a different state after the client sends the first packet.
#  -- From wiki.vg editors- IRC #mcdevs @ chat.freenode.net

# ----------------------
# Handshaking Mode Packets: Serverbound
# ----------------------


class Handshake(Packet):
    def __init__(self, data):
        self.protocol_version, data = VarInt.decode(data)
        self.server_address, data = decode_string(data)
        self.server_port = struct.unpack(">H", data[:2])
        self.next_state, _ = VarInt.decode(data[2:])


class LegacyServerListPing(Packet):
    pass

# ----------------------
# Status Mode Packets: Clientbound
# ----------------------


@dataclass
class Response(Packet):
    response: str
    
    def to_bytes(self):
        return encode_string(self.response)


@dataclass
class Pong(Packet):
    payload: int
    
    def to_bytes(self):
        return struct.pack(">q", self.payload)[0]

# ----------------------
# Status Mode Packets: Serverbound
# ----------------------


class Request(Packet):
    pass


class Ping(Packet):
    def __init__(self, data):
        self.payload = struct.unpack(">q", data)[0]

# ----------------------
# Login Mode Packets: Clientbound
# ----------------------


@dataclass
class DisconnectLogin(Packet):
    reason: str
    
    def to_bytes(self):
        return encode_string(self.reason)


@dataclass
class EncryptionRequest(Packet):
    server_id: str
    pubkey: bytes
    verify_token: bytes

    def to_bytes(self):
        return encode_string(self.server_id) + \
            VarInt.encode(len(self.pubkey)) + \
            self.pubkey + \
            VarInt.encode(len(self.verify_token)) + \
            self.verify_token


@dataclass
class LoginSuccess(Packet):
    uuid: str
    username: str
    
    def to_bytes(self):
        return encode_string(self.uuid) + encode_string(self.username)


@dataclass
class SetCompression(Packet):
    threshold: int
    
    def to_bytes(self):
        return VarInt.encode(self.threshold)


@dataclass
class LoginPluginRequest(Packet):
    message_id: int
    channel: str
    data: bytes
    
    def to_bytes(self):
        return VarInt.encode(self.message_id) + encode_string(self.channel) + self.data

# ----------------------
# Login Mode Packets: Serverbound
# ----------------------


class LoginStart(Packet):
    def __init__(self, packet):
        self.username, _ = decode_string(packet)


class EncryptionResponse(Packet):
    def __init__(self, packet):
        secret_len, packet = VarInt.decode(packet)
        self.secret = packet[:secret_len]
        token_len, packet = VarInt.decode(packet)
        self.token = packet[:token_len]


class LoginPluginResponse(Packet):
    def __init__(self, packet):
        self.message_id, packet = VarInt.decode(packet)
        self.successful = struct.unpack(">?", packet[0])
        self.data = packet[1:]


# ----------------------
# Play Mode Packets: Clientbound
# ----------------------


