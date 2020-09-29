import struct
from dataclasses import dataclass

from typing import Tuple, Union

# Python ints are variable length, which means there's no fixed size.
# Typical programming language implementation exploits the sign bit moving
# when doing bitwise shifts, but that's not possible here.
# To force an int32-like type, we use the `struct` module to make it fit.

# Struct cheat sheet
# < - LE
# > - BE                  Python Type Width  Range
# c - char                bytes[1]    1      [ASCII character]
# b - signed char         int         1      -128 - 127
# B - unsigned char       int         1         0 - 255
# ? - bool                bool        1      True / False
# h - short               int         2      -32768 - 32767
# H - unsigned short      int         2           0 - 65535
# i - int                 int         4      -2147483648 - 2147483647  # Also duplicated by l (long)
# I - unsigned int        int         4                0 - 2147483647  # Also duplicated by L (unsigned long)
# q - long                int         8      -9223372036854775808 - 9223372036854775807
# Q - unsigned long       int         8                         0 - 18446744073709551615
# e - half float          float       2      +/- 6.1e-005 - 6.5e+004
# f - float               float       4      +/- 1.4e-045 - 3.4e+038
# d - double              float       8      +/- 5.0e-324 - 1.8e+308


class VarInt:
    @staticmethod
    def decode(sock):
        """
        Read a VarInt from a socket or bytes object. Returns the number, alongside the rest of the data (if passed a
        bytes object).
    
        :param sock: Socket or a bytes to read a VarInt from.
        :raises OverflowError: The VarInt we read was too large.
        :raises TypeError: We got back b''/EOF from a socket.
        :raises IndexError: We tried to read b'' from a bytes input.
        :return: The number that was read. If input was a string-like, return the rest of the string as well.
        """
        n_bytes = 0
        number = 0
        byte = 128  # The byte we are reading in
        while (byte & 0x80) != 0:
            if n_bytes > 4:
                raise OverflowError("VarInt too large")
            n_bytes += 1
            if isinstance(sock, bytes):
                byte = sock[0]
                sock = sock[1:]
            else:
                byte = ord(sock.recv(1))
            value = byte & 0x7f
            number |= value << (7 * n_bytes)  # In-place bitwise OR operation
        if number > 2**31-1:
            number -= 2**32
        if isinstance(sock, bytes):
            return number, sock
        else:
            return number
    
    @staticmethod
    def encode(number):
        """
        Write a VarInt to a string.
    
        :param number: Number to encode as a VarInt.
        :raises struct.error: The provided number is outside the bounds for this type.
        :return: The encoded VarInt.
        """
        number = struct.unpack(">I", struct.pack(">i", number))[0]
        out = b""
        while True:
            part = number & 0x7f
            number = number >> 7
            if number != 0:
                part |= 0x80  # In-place OR operation
                out += part.to_bytes(1, byteorder="big")
            else:
                out += part.to_bytes(1, byteorder="big")
                return out
    

class VarLong:
    @staticmethod
    def decode(sock):
        """
        Read a VarLong from a socket or bytes object. Returns the number, alongside the rest of the data (if passed a
        bytes object).
    
        :param sock: Socket or a bytes to read a VarLong from.
        :raises OverflowError: The VarLong we read was too large.
        :raises TypeError: We got back b''/EOF from a socket.
        :raises IndexError: We tried to read b'' from a bytes input.
        :return: The number that was read. If input was a string-like, return the rest of the string as well.
        """
        n_bytes = 0
        number = 0
        byte = 128  # The byte we are reading in
        while (byte & 0x80) != 0:
            if n_bytes > 9:
                raise OverflowError("VarLong too large")
            n_bytes += 1
            if isinstance(sock, bytes):
                byte = sock[0]
                sock = sock[1:]
            else:
                byte = ord(sock.recv(1))
            value = byte & 0x7f
            number |= value << (7 * n_bytes)  # In-place bitwise OR operation
        if number > 2**63-1:
            number -= 2**64
        if isinstance(sock, bytes):
            return number, sock
        else:
            return number
    
    @staticmethod
    def encode(number):
        """
        Write a VarLong to a string.
    
        :param number: Number to encode as a VarLong.
        :raises struct.error: The provided number is outside the bounds for this type.
        :return: The encoded VarLong.
        """
        print()
        number = struct.unpack(">Q", struct.pack(">q", number))[0]
        out = b""
        while True:
            part = number & 0x7f
            number = number >> 7
            if number != 0:
                part |= 0x80  # In-place OR operation
                out += part.to_bytes(1, byteorder="big")
            else:
                out += part.to_bytes(1, byteorder="big")
                return out
    

@dataclass
class Position:
    x: int
    y: int
    z: int
    
    def _encode(self, new_format):
        out = 0
        if new_format:
            out = ((self.x & 0x3FFFFFF) << 38) | ((self.z & 0x3FFFFFF) << 12) | (self.y & 0xFFF)
            # Thanks to the docs on wiki.vg #mcdevs for giving this helpful copy-paste piece of code :)
        else:
            out = ((self.x & 0x3FFFFFF) << 38) | ((self.y & 0xFFF) << 26) | (self.z & 0x3FFFFFF)
            # And again lol
        return out.to_bytes(8, "big")

    def encode(self):
        """
        Encode this Position into network byte format, using the new 1.14+ format. Call encode_old() for old format.

        :return: The encoded Position.
        """
        return self._encode(True)

    def encode_old(self):
        """
        Encode this Position into network byte format, using the old 1.13 and earlier format. Call encode() for new
        format.

        :return: The encoded Position.
        """
        return self._encode(False)

    @classmethod
    def _from_bytes(cls, data: Union[bytes, int], new_format):
        if isinstance(data, bytes):
            data = struct.unpack(">Q", data)[0]
        
        if new_format:
            x = data >> 38
            y = data & 0xFFF
            z = (data & 0x0000_003F_FFFF_F000) >> 26
        else:
            x = data >> 38
            z = data & 0x3FFFFFF
            y = (data & 0x0000_003F_FC00_0000) >> 26
        
        if x >= 2**25:
            x -= 2**26
        if y >= 2**25:
            y -= 2**26
        if z >= 2**25:
            z -= 2**26
        return cls(x, y, z)

    @classmethod
    def from_bytes(cls, data: Union[bytes, int]):
        """
        Return a Position object from the encoded bytes (or int) using the new 1.14+ format. Call from_bytes_old()
        for old format.
        
        :param data: The bytes or int of this position.
        :return: The corresponding Position.
        """
        return cls._from_bytes(data, True)
    
    @classmethod
    def from_bytes_old(cls, data: Union[bytes, int]):
        """
        Return a Position object from the encoded bytes (or int) using the old 1.13 and earlier format. Call
        from_bytes() for new format.

        :param data: The bytes or int of this position.
        :return: The corresponding Position.
        """
        return cls._from_bytes(data, False)


class EntityVelocityType:
    @staticmethod
    def decode(data: Union[bytes, int]):
        """
        Takes an encoded Velocity value and returns its m/s speed.

        :param data: The encoded Velocity
        :return: The velocity, in m/s
        """
        if isinstance(data, bytes):
            data = struct.unpack(">h", data)[0]
        return data / 400
    
    @staticmethod
    def encode(value: float):
        """
        Takes a Velocity value in m/s and converts to the network EntityVelocity format (int16).
        
        :param value: The value to convert.
        :return: The converted bytes.
        """
        return round(value*400).to_bytes(2, "big")
    

class String:
    @staticmethod
    def decode(packet: bytes) -> Tuple[str, bytes]:
        """
        Decode a String from a packet and return the string and the remainder of the packet.
        
        :param packet: Packet to parse the next String from.
        :return: The String that was read, along with the rest of the packet.
        """
        length, packet = VarInt.decode(packet)
        s = packet[:length]
        return s, packet[length:]
    
    @staticmethod
    def encode(s) -> bytes:
        """
        Encode a String to corresponding bytes[] object.
        
        :param s: String to encode.
        :return: Encoded String.
        """
        return VarInt.encode(len(s)) + s.encode("utf-8")


class UUID:
    @staticmethod
    def encode(uuid: Union["UUID", str]):
        """
        Return an encoded UUID.

        :param uuid: UUID to encode. Dashes don't matter, nor capitalization.
        :return: Encoded UUID.
        """
        if not isinstance(uuid, int):
            uuid = uuid.replace("-", "")
            uuid = uuid.lower()
            upper = int(uuid[:16], base=16)
            lower = int(uuid[16:], base=16)
        else:
            upper = (uuid & 0xFFFFFFFFFFFFFFFF0000000000000000) >> 64
            lower = uuid & 0x0000000000000000FFFFFFFFFFFFFFFF
        return struct.pack(">QQ", upper, lower)

    @staticmethod
    def bytes_to_str(data: bytes):
        """
        Convert a UUID from wire format to a str (without hyphens).
    
        :param data: UUID to parse.
        :return: Decoded UUID.
        """
        upper, lower = struct.unpack(">QQ", data)
        return (hex(upper)[2:]) + (hex(lower)[2:])

    @staticmethod
    def bytes_to_int128(data: bytes):
        """
        Convert a UUID from wire format to a single 128-bit integer.
        
        :param data: UUID to parse.
        :return: Decoded UUID.
        """
        upper, lower = struct.unpack(">QQ", data)
        return (upper << 64) | lower

    @staticmethod
    def bytes_to_int64(data: bytes):
        """
        Convert a UUID from wire format to a pair of 64-bit integers.
        
        :param data: UUID to parse.
        :return: Decoded UUID.
        """
        uuid_upper = struct.unpack(">Q", data[:16])[0]
        uuid_lower = struct.unpack(">Q", data[16:])[0]
        return uuid_upper, uuid_lower


# ----------
# Data types beyond this point only exist as dummy types, to be used by Packet.to_bytes()
# ----------


class StructType:
    code = None
    size = None


class Boolean(StructType, bool):
    code = "?"
    size = 1


class Byte(StructType, int):
    code = "b"
    size = 1


class UnsignedByte(StructType, int):
    code = "B"
    size = 1


class Short(StructType, int):
    code = "h"
    size = 2


class UnsignedShort(StructType, int):
    code = "H"
    size = 2


class Int(StructType, int):
    code = "i"
    size = 4


class Long(StructType, int):
    code = "q"
    size = 4


class Float(StructType, float):
    code = "f"
    size = 4


class Double(StructType, float):
    code = "d"
    size = 8


Chat = String
Identifier = String


class Angle(StructType):
    # todo: this should probably be above, with encode/decode staticmethods
    code = "b"
    size = 1


