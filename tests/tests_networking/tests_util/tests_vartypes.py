import random
import socket
import struct

from networking.util.vartypes import *


def test_encode_varint():
    # standard VarInt values
    assert encode_varint(0) == b"\x00"
    assert encode_varint(1) == b"\x01"
    assert encode_varint(2) == b"\x02"
    assert encode_varint(127) == b"\x7f"
    assert encode_varint(128) == b"\x80\x01"
    assert encode_varint(255) == b"\xff\x01"
    assert encode_varint(2147483647) == b"\xff\xff\xff\xff\x07"
    assert encode_varint(-1) == b"\xff\xff\xff\xff\x0f"
    assert encode_varint(-2147483648) == b"\x80\x80\x80\x80\x08"
    
    # Make sure limits are enforced
    assert isinstance(encode_varint(2147483648), struct.error)
    assert isinstance(encode_varint(-2147483649), struct.error)
    assert isinstance(encode_varint(23489062762390), struct.error)
    assert isinstance(encode_varint(-12045763498527), struct.error)
    assert isinstance(encode_varint(324576230948720987534456), struct.error)
    assert isinstance(encode_varint(-293786529387462938547564), struct.error)


def test_decode_varint_bytes():
    # Test standard VarInt values with bytes object
    assert decode_varint(b"\x00") == 0, b""
    assert decode_varint(b"\x01") == 1, b""
    assert decode_varint(b"\x02") == 2, b""
    assert decode_varint(b"\x7f") == 127, b""
    assert decode_varint(b"\x80\x01") == 128, b""
    assert decode_varint(b"\xff\x01") == 255, b""
    assert decode_varint(b"\xff\xff\xff\xff\x07") == 2147483647, b""
    assert decode_varint(b"\xff\xff\xff\xff\x0f") == -1, b""
    assert decode_varint(b"\x80\x80\x80\x80\x08") == -2147483648, b""
    
    # Test invalid inputs
    assert isinstance(decode_varint(b"\xff\xff\xff\xff\xff\xff"), OverflowError)
    assert isinstance(decode_varint(b"\x80\x80\x80\x80\x80\x80"), OverflowError)
    assert isinstance(decode_varint(b"\xff"), TypeError)
    assert isinstance(decode_varint(b""), IndexError)
    
    # Test returning rest of bytes[]
    assert decode_varint(b"\x00OwO") == 0, b"OwO"
    assert decode_varint(b"\xff\x01Important Packet Here") == 255, b"Important Packet Here"
    assert decode_varint(b"\xff\xff\xff\xff\x07\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00") == \
           2147483647, b"\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00"
    assert decode_varint(b"\x80\x80\x80\x80\x081\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2") == \
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
    assert decode_varint(serv_c) == 0
    assert decode_varint(serv_c) == 1
    assert decode_varint(serv_c) == 2
    assert decode_varint(serv_c) == 127
    assert decode_varint(serv_c) == 128
    assert decode_varint(serv_c) == 255
    assert decode_varint(serv_c) == 2147483647
    assert decode_varint(serv_c) == -1
    assert decode_varint(serv_c) == -2147483648
    
    # Test too large VarInt, then test EOF
    client.send(b"\xff\xff\xff\xff\xff\xca'\xdf")
    assert isinstance(decode_varint(serv_c), OverflowError)
    assert serv_c.recv(4096) == b"\xca'\xdf"
    client.close()
    assert isinstance(decode_varint(serv_c), TypeError)


def test_encode_varlong():
    # standard VarLong values
    assert encode_varlong(0) == b"\x00"
    assert encode_varlong(1) == b"\x01"
    assert encode_varlong(2) == b"\x02"
    assert encode_varlong(127) == b"\x7f"
    assert encode_varlong(128) == b"\x80\x01"
    assert encode_varlong(255) == b"\xff\x01"
    assert encode_varlong(2147483647) == b"\xff\xff\xff\xff\x07"
    assert encode_varlong(9223372036854775807) == b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f"
    assert encode_varlong(-1) == b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01"
    assert encode_varlong(-2147483648) == b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01"
    assert encode_varlong(-9223372036854775808) == b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01"
    
    # invalid VarLong values
    assert isinstance(encode_varlong(349876025734624589762384762352), struct.error)
    assert isinstance(encode_varlong(-104875623985426394857623954873), struct.error)
    

def test_decode_varlong_bytes():
    assert decode_varint(b"\x00") == 0, b""
    assert decode_varint(b"\x01") == 1, b""
    assert decode_varint(b"\x02") == 2, b""
    assert decode_varint(b"\x7f") == 127, b""
    assert decode_varint(b"\x80\x01") == 128, b""
    assert decode_varint(b"\xff\x01") == 255, b""
    assert decode_varint(b"\xff\xff\xff\xff\x07") == 2147483647, b""
    assert decode_varint(b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f") == 9223372036854775807, b""
    assert decode_varint(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01") == -1, b""
    assert decode_varint(b"\x80\x80\x80\x80\xf8\xff\xff\xff\xff\x01") == -2147483648, b""
    assert decode_varint(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x01") == -9223372036854775808, b""
    
    # invalid inputs
    assert isinstance(decode_varlong(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x80"), OverflowError)
    assert isinstance(decode_varlong(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"), OverflowError)
    assert isinstance(decode_varlong(b"\xff"), TypeError)
    assert isinstance(decode_varlong(b""), IndexError)
    
    # Test returning rest of bytes[]
    assert decode_varlong(b"\x00OwO") == 0, b"OwO"
    assert decode_varlong(b"\xff\x01Important Packet Here") == 255, b"Important Packet Here"
    assert decode_varlong(b"\xff\xff\xff\xff\xff\xff\xff\xff\x7f\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00") == \
           9223372036854775807, b"\x16\xea\xda}\xf8\xa7\x8a\xdc\x83\xa2\xd3^\xb4\x00\x00"
    assert decode_varlong(b"\x80\x80\x80\x80\x80\x80\x80\x80\x80\x011\xa8\xe2\xad\xa4\xad\xad\xac\x1bz\xba\xf2") == \
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
    assert decode_varlong(serv_c) == 0
    assert decode_varlong(serv_c) == 1
    assert decode_varlong(serv_c) == 2
    assert decode_varlong(serv_c) == 127
    assert decode_varlong(serv_c) == 128
    assert decode_varlong(serv_c) == 255
    assert decode_varlong(serv_c) == 2147483647
    assert decode_varlong(serv_c) == 9223372036854775807
    assert decode_varlong(serv_c) == -1
    assert decode_varlong(serv_c) == -2147483648
    assert decode_varlong(serv_c) == -9223372036854775808
    
    client.send(b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xca'\xdf")
    assert isinstance(decode_varlong(serv_c), OverflowError)
    assert serv_c.recv(4096) == b"\xca'\xdf"
    client.close()
    assert isinstance(decode_varlong(serv_c), TypeError)
