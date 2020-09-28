import struct


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
    @classmethod
    def decode(cls, sock):
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
    
    @classmethod
    def encode(cls, number):
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
    @classmethod
    def decode(cls, sock):
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
    
    @classmethod
    def encode(cls, number):
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
    
