import random
import socket
import struct

from networking.util.vartypes import VarInt, VarLong


def test_encode_varint():
    # standard VarInt values
    assert VarInt.encode(0) == b"\x00"
    assert VarInt.encode(1) == b"\x01"
    assert VarInt.encode(2) == b"\x02"
    assert VarInt.encode(127) == b"\x7f"
    assert VarInt.encode(128) == b"\x80\x01"
    assert VarInt.encode(255) == b"\xff\x01"
    assert VarInt.encode(2147483647) == b"\xff\xff\xff\xff\x07"
    assert VarInt.encode(-1) == b"\xff\xff\xff\xff\x0f"
    assert VarInt.encode(-2147483648) == b"\x80\x80\x80\x80\x08"
    
    # Make sure limits are enforced
    assert isinstance(VarInt.encode(2147483648), struct.error)
    assert isinstance(VarInt.encode(-2147483649), struct.error)
    assert isinstance(VarInt.encode(23489062762390), struct.error)
    assert isinstance(VarInt.encode(-12045763498527), struct.error)
    assert isinstance(VarInt.encode(324576230948720987534456), struct.error)
    assert isinstance(VarInt.encode(-293786529387462938547564), struct.error)


def test_decode_varint_bytes():
    # Test standard VarInt values with bytes object
    assert VarInt.decode(b"\x00") == 0, b""
    assert VarInt.decode(b"\x01") == 1, b""
    assert VarInt.decode(b"\x02") == 2, b""
    assert VarInt.decode(b"\x7f") == 127, b""
    assert VarInt.decode(b"\x80\x01") == 128, b""
    assert VarInt.decode(b"\xff\x01") == 255, b""
    assert VarInt.decode(b"\xff\xff\xff\xff\x07") == 2147483647, b""
    assert VarInt.decode(b"\xff\xff\xff\xff\x0f") == -1, b""
    assert VarInt.decode(b"\x80\x80\x80\x80\x08") == -2147483648, b""
    
    # Test invalid inputs
    assert isinstance(VarInt.decode(b"\xff\xff\xff\xff\xff\xff"), OverflowError)
    assert isinstance(VarInt.decode(b"\x80\x80\x80\x80\x80\x80"), OverflowError)
    assert isinstance(VarInt.decode(b"\xff"), TypeError)
    assert isinstance(VarInt.decode(b""), IndexError)
    
    # Test returning rest of bytes[]
    assert VarInt.decode(b"\x00OwO") == 0, b"OwO"
    assert VarInt.decode(b"\xff\x01Important Packet Here") == 255, b"Important Packet Here"
    assert VarInt.decode(b"\xff\xff\xff\xff\x07\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00") == \
           2147483647, b"\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00"
    assert VarInt.decode(b"\x80\x80\x80\x80\x081\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2") == \
           -2147483648, b"1\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2"


def test_decode_varint_socket():
    serv = socket.socket()
    while True:
        port = random.randint(1024, 65535)  # Binding to ports below 1024 requires privileges on POSIX-based OSes
        try:
            serv.bind(("127.1", port))
        except:
            continue
        else:
            break
    serv.listen(1)
    client = socket.create_connection(("127.1", port))
    serv_c, a = serv.accept()
    
    # Send all of our data in one go
    # This has the advantage of also testing the rest of the data on the stream is preserved
    client.send(b"\x00"
                b"\x01"
                b"\x02"
                b"\x7f"
                b"\x80\x01"
                b"\xff\x01"
                b"\xff\xff\xff\xff\x07"
                b"\xff\xff\xff\xff\x0f"
                b"\x80\x80\x80\x80\x08")
    assert VarInt.decode(serv_c) == 0
    assert VarInt.decode(serv_c) == 1
    assert VarInt.decode(serv_c) == 2
    assert VarInt.decode(serv_c) == 127
    assert VarInt.decode(serv_c) == 128
    assert VarInt.decode(serv_c) == 255
    assert VarInt.decode(serv_c) == 2147483647
    assert VarInt.decode(serv_c) == -1
    assert VarInt.decode(serv_c) == -2147483648
    
    # Test too large VarInt, then test EOF
    client.send(b"\xff\xff\xff\xff\xff\xca'\xdf")
    assert isinstance(VarInt.decode(serv_c), OverflowError)
    assert serv_c.recv(4096) == b"\xca'\xdf"
    client.close()
    assert isinstance(VarInt.decode(serv_c), TypeError)


def test_encode_varlong():
    # standard VarLong values
    assert VarLong.encode(0) == b"\x00"
    assert VarLong.encode(1) == b"\x01"
    assert VarLong.encode(2) == b"\x02"
    assert VarLong.encode(127) == b"\x7f"
    assert VarLong.encode(128) == b"\x80\x01"
    assert VarLong.encode(255) == b"\xff\x01"
    assert VarLong.encode(2147483647) == b"\xff\xff\xff\xff\x07"
    assert VarLong.encode(9223372036854775807) == b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f"
    assert VarLong.encode(-1) == b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01"
    assert VarLong.encode(-2147483648) == b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01"
    assert VarLong.encode(-9223372036854775808) == b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01"
    
    # invalid VarLong values
    assert isinstance(VarLong.encode(349876025734624589762384762352), struct.error)
    assert isinstance(VarLong.encode(-104875623985426394857623954873), struct.error)
    

def test_decode_varlong_bytes():
    assert VarInt.decode(b"\x00") == 0, b""
    assert VarInt.decode(b"\x01") == 1, b""
    assert VarInt.decode(b"\x02") == 2, b""
    assert VarInt.decode(b"\x7f") == 127, b""
    assert VarInt.decode(b"\x80\x01") == 128, b""
    assert VarInt.decode(b"\xff\x01") == 255, b""
    assert VarInt.decode(b"\xff\xff\xff\xff\x07") == 2147483647, b""
    assert VarInt.decode(b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f") == 9223372036854775807, b""
    assert VarInt.decode(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01") == -1, b""
    assert VarInt.decode(b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01") == -2147483648, b""
    assert VarInt.decode(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01") == -9223372036854775808, b""
    
    # invalid inputs
    assert isinstance(VarLong.decode(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80"), OverflowError)
    assert isinstance(VarLong.decode(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"), OverflowError)
    assert isinstance(VarLong.decode(b"\xff"), TypeError)
    assert isinstance(VarLong.decode(b""), IndexError)
    
    # Test returning rest of bytes[]
    assert VarLong.decode(b"\x00OwO") == 0, b"OwO"
    assert VarLong.decode(b"\xff\x01Important Packet Here") == 255, b"Important Packet Here"
    assert VarLong.decode(b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00") == \
           9223372036854775807, b"\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00"
    assert VarLong.decode(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x011\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2") == \
           -9223372036854775808, b"1\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2"


def test_decode_varlong_socket():
    serv = socket.socket()
    while True:
        port = random.randint(1024, 65535)
        try:
            serv.bind(("127.1", port))
        except:
            continue
        else:
            break
    serv.listen(1)
    client = socket.create_connection(("127.1", port))
    serv_c, a = serv.accept()
    
    client.send(b"\x00"
                b"\x01"
                b"\x02"
                b"\x7f"
                b"\x80\x01"
                b"\xff\x01"
                b"\xff\xff\xff\xff\x07"
                b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f"
                b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01"
                b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01"
                b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01")
    assert VarLong.decode(serv_c) == 0
    assert VarLong.decode(serv_c) == 1
    assert VarLong.decode(serv_c) == 2
    assert VarLong.decode(serv_c) == 127
    assert VarLong.decode(serv_c) == 128
    assert VarLong.decode(serv_c) == 255
    assert VarLong.decode(serv_c) == 2147483647
    assert VarLong.decode(serv_c) == 9223372036854775807
    assert VarLong.decode(serv_c) == -1
    assert VarLong.decode(serv_c) == -2147483648
    assert VarLong.decode(serv_c) == -9223372036854775808
    
    client.send(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xca'\xdf")
    assert isinstance(VarLong.decode(serv_c), OverflowError)
    assert serv_c.recv(4096) == b"\xca'\xdf"
    client.close()
    assert isinstance(VarLong.decode(serv_c), TypeError)
