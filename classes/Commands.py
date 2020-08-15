# coding=utf-8
""" API module holding all the registered commands. Also contains base command classed. """
# TODO: to whoever has an idea on how imports work, please import the main module here. Then update all the objects with
# the ChatRoomProtocol class. Thanks!


class Command:
    def __init__(self, name: str, permissionLevel: int, action: callable(object, str)):
        self._name = name.lower()
        self._level = permissionLevel
        self._action = action

    def onCommand(self, permlevel: int, label: str, connection: object, *args: str) -> bool:
        """ Returns true if the command was fired, false otherwise """
        if label.lower() == self._name and permlevel >= self._level:
            self._action(connection, *args)
            return True
        else:
            return False


def _cmd_me(c: object, *args):
    c.factory.send_chat(u"\u00a78*%s \u00a77" % c.display_name + ' '.join(*args))


def _cmd_ver(c: object, *args):
    c.send_packet("chat_message",
                  c.buff_type.pack_chat("\u00a7b Made with lover by the mcpy team") + c.buff_type.pack('B', 0))


REGISTERED_COMMANDS: [Command] = [Command("me", 0, _cmd_me), Command("version", 0, _cmd_ver)]
