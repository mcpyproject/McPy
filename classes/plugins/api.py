from classes.network import Connection

def chat_message(message: str):
    Connection.NetworkController.send_packet(packet_type=Connection.PacketType.CHAT_MESSAGE,message=message)
