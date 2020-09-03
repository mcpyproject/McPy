# coding=utf-8
# Import fundamental libraries required for the next check
import logging
import sys

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal(
        'McPy needs Python version 3.8.0 or higher to run! Current version is {}.{}.{}'.format(sys.version_info.major,
                                                                                               sys.version_info.minor,
                                                                                               sys.version_info.micro))
    sys.exit(-2)

# Import general libraries
import argparse
import gc
import multiprocessing
import os
import random
import time
from queue import Empty, Full  # multiprocessing.Queue() full and empty exception
from quarry.net import server
from twisted.internet import reactor


def send_task(func, args: list, kwargs: dict, data_in: multiprocessing.Queue, task_id: int) -> [int, None]:
    """
    Send a task to be executed by workers
    :param func: Function to be executed: must not be a coroutine
    :param args: Arguments for the function: a list or tuple of items
    :param kwargs: Keyword arguments for the function: a dict of items
    :param data_in: The queue down which items will be sent
    :param task_id: The ID for the task: not optional
    :return: None, or 1 if queue was full
    """
    task_data = {
        'func': func,
        'args': args,
        'kwargs': kwargs
    }
    try:
        td = task_data
        td["id"] = task_id
        data_in.put_nowait(task_data)  # If queue is full, throw queue.Full exception
    except Full:
        logging.warning("Queue {0} is full!".format(data_in.__name__))
        return 1
    TASK_LIST[task_id] = task_data
    return


def get_all_completed_tasks(queue_in_use):
    """
    Given a Queue object, will return all tasks for that queue
    :param queue_in_use: Queue object to have items returned for
    """
    while True:  # Old statement was too unreliable, so catch the exception and break
        try:
            yield queue_in_use.get(False)
        except Empty:
            break


def add_one(a):
    """
    Simple function used in early phases of dev
    :param a: Number to add one to
    :return: Number plus 1
    """
    return a + 1


def get_rand_task_id() -> int:
    """
    Return a random task ID between 1 and 10000000
    :return: Number between 1 and 10000000
    """
    taskId = round(random.random() * 10000000)  # Generate a random ID for the task
    return taskId


def return_task_id(task_id_list: list, task_id: int = None):
    """
    Add item to the task ID list, and return the new list and a ID
    :param task_id_list: List to add the task to
    :param task_id: None or a int: if none, a task ID will be generated
    :return: Task ID list, and the task ID
    """
    if not task_id:
        task_id = get_rand_task_id()
    task_id_list.append(task_id)
    return task_id_list, task_id


# The next two classes are from https://quarry.readthedocs.io
# noinspection PyMissingOrEmptyDocstring
class ChatRoomProtocol(server.ServerProtocol):
    def player_joined(self):
        super(ChatRoomProtocol, self).player_joined()

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
        # Send Brand packet
        self.send_packet("plugin_message",
                         self.buff_type.pack_string("minecraft:brand"),
                         self.buff_type.pack_string("McPy/0.0.1-alpha"))  # TODO don't make this hardcoded
        # Send server difficulty packet
        self.send_packet("server_difficulty",
                         self.buff_type.pack("B?",
                                             0,  # difficulty = peaceful
                                             True))  # difficulty locked
        # Send player ability packet
        self.send_packet("player_abilities",
                         self.buff_type.pack("bff",
                                             0x00,  # no flags set
                                             0.05,  # default speed
                                             0.1))  # default FOV
        # TODO inbound Client settings packet
        # Held item change packet
        self.send_packet("held_item_change",
                         self.buff_type.pack("b",
                                             0x00))  # leftmost item
        # TODO declare recipes (this should be automated, no sane person would handwrite that)
        # TODO tags (maybe in combination with the recipes and declaring them in a datapack)
        # TODO entity status (what is that?)
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

        self._players.append([self.uuid, self.display_name])
        # self.update_tablist()

        # Send current time & day
        self.send_day_time_update()

        # Announce player joined
        self.factory.send_chat(u"\u00a7e%s has joined." % self.display_name)

    def player_left(self):
        super(ChatRoomProtocol, self).player_left()

        self._players.remove([self.uuid, self.display_name])
        # self.update_tablist()
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
        log(self.logging, chat_msg, "Chat")

    def send_day_time_update(self):
        self.send_packet("time_update", self.buff_type.pack(
            "QQ",  # Field one will be a int (or any of Java's integer representations), and so will field 2
            self.sharedManager['totalTime'],  # Field one is the total overall game time
            self.sharedManager['dayTime']  # Field two is the current time of day
        ))

    def update_tablist(self):
        parsed_player_list = []
        for item in self._players:
            parse_player_list = [item[0], item[1], 0, 3, 0, True, item[1]]
            parsed_player_list.append(parse_player_list)
        self.send_packet(self.buff_type.pack(
            "iia",
            0,
            len(self._players),
            parsed_player_list
        ))


# noinspection PyMissingOrEmptyDocstring
class ChatRoomFactory(server.ServerFactory):
    def __init__(self, shared_manager, players, logging_queue: multiprocessing.Queue):
        super(ChatRoomFactory, self).__init__()
        self.protocol = ChatRoomProtocol
        self.protocol.sharedManager = self.sharedManager = shared_manager
        self.protocol._players = self._players = players
        self.protocol.logging = logging_queue
        self.motd = "Chat Room Server"  # Later customizable

    def send_chat(self, message):
        for player in self.players:
            player.send_packet("chat_message", player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0))

    def send_new_tablist(self, tablist):
        for player in self.players:
            player.send_packet("")


def log(logging_queue: multiprocessing.Queue, message, _id, _type="info", exception=None):
    """
    TODO: fill this in
    :param logging_queue:
    :param message:
    :param _id:
    :param _type:
    :param exception:
    """
    logging_queue.put({
        "type": _type,
        "id": str(_id),
        "message": message,
        "exception": exception
    })


def worker(in_queue: multiprocessing.Queue, out_queue: multiprocessing.Queue, logging_queue: multiprocessing.Queue,
           workerId: str):
    """
    Worker function: to be executed by all new workers spawned with multiprocessing
    :param in_queue: Queue that new tasks will be obtained
    :param out_queue: Queue that task results will be obtained
    :param logging_queue: TODO: fill this in
    :param workerId: ID of the worker
    """
    log(logging_queue, "Worker started up.", workerId)
    while True:
        try:
            item: [dict, str] = in_queue.get()  # Waits for a new item to appear on the queue
        except KeyboardInterrupt:
            out_queue.put(None)
            break
        if item is None:  # Sending None down the pipe stops the first worker that grabs it: send it as many times as
            # there are workers and they'll all stop: this is how McPy shuts all of them down safely
            out_queue.put(None)
            break
        elif isinstance(item, str):
            if item.startswith("gc"):
                try:
                    if int(item[2]) in (0, 1, 2):
                        gc.collect(int(item[2]))
                except TypeError:
                    pass
            continue
        func = item["func"]
        args = item["args"]
        kwargs = item["kwargs"]
        # noinspection PyBroadException
        try:
            result = func(*args, **kwargs)  # Calls the requested function: MUST NOT BE DEFINED WITH async def
        except Exception as ex:
            log(logging_queue, "Exception in Thread", workerId, _type="exception", exception=ex)
            result = "error"  # idk the best way to define a error result
        out_queue.put({
            "request": item,
            "result": result
        })
    log(logging_queue, "Tasks completed", workerId)


def networker(shared_manager, players, logging_queue: multiprocessing.Queue):
    """
    TODO: fill this in
    :param shared_manager:
    :param players:
    :param logging_queue:
    """
    factory = ChatRoomFactory(shared_manager, players, logging_queue)
    factory.motd = "Chat Room"
    factory._logging = logging_queue
    logging.info("Starting networking worker")
    listener = ("0.0.0.0", 25565)
    try:
        factory.listen(*listener)
        log(logging_queue, "Startup done! Listening on {0[0]}:{0[1]}".format(listener), "Networker")
        # noinspection PyUnresolvedReferences
        reactor.run()
    except Exception as ex:
        log(logging_queue, "Exception in networking thread! Restarting...", "Networker", _type="exception",
            exception=ex)
        time.sleep(5)
        networker(shared_manager, players, logging_queue)


def main():
    # Here start the server :D
    logging.info("Trying to find number of available cores")
    try:
        avail_cores = len(os.sched_getaffinity(0))
    except AttributeError:
        # Fix for windows, which doesnt support getaffinity
        logging.warning(
            "Falling back to multiprocessing cpu_count to calc cores. Most likely getaffinity is not supported on "
            "your OS")
        avail_cores = multiprocessing.cpu_count()

    if avail_cores < 2:
        avail_cores = 2  # Force at least 2 workers, just in case only one core is available: one worker to do all the
        # major tasks and one to just take care of networking: THIS WILL BE LAGGY: VERY LAGGY
    logging.info("Found {0} cores available!".format(avail_cores))
    workers = []
    gc.collect(2)
    gc.disable()
    for _ in range(avail_cores - 1):  # Reserve one worker for the networking thread
        del _
        worker_id = str(round(random.random() * 100000))
        logging.info("Starting worker ID {0}".format(worker_id))
        func_args = (TASK_QUEUE, DONE_QUEUE, LOGGING_QUEUE, worker_id)
        p = multiprocessing.Process(target=worker, args=func_args)
        p.start()
        logging.info("Started worker.")
        workers.append(p)
    shared_manager = multiprocessing.Manager().dict()
    shared_manager['totalTime'] = 0  # Time of day in ticks
    shared_manager['dayTime'] = 0  # Number of players online
    players = multiprocessing.Manager().list()
    logging.info("Starting networking worker")
    func_args = (shared_manager, players, LOGGING_QUEUE)
    networking_process = multiprocessing.Process(target=networker, args=func_args)
    networking_process.start()
    logging.info("Started worker.")
    gc.enable()
    try:
        tick = 0
        while True:
            # print("Tick = %d" % tick)
            task_ids = []
            start_tick_at = time.time()
            finish_tick_at = start_tick_at + 0.05  # add 50 milliseconds or one tick
            # TODO The next 4 lines are here only for TESTING, don't forget to remove these in the futur
            task_ids, tid = return_task_id(task_ids)
            send_task(add_one, [shared_manager['totalTime']], {}, TASK_QUEUE, tid)
            task_ids, tid = return_task_id(task_ids)
            send_task(add_one, [shared_manager['dayTime']], {}, TASK_QUEUE, tid)

            shared_manager['totalTime'] += 1
            shared_manager['dayTime'] += 1
            shared_manager['dayTime'] %= 24000
            try:
                # noinspection PyArgumentEqualDefault
                # The goal here is to loop over each element in DONE_QUEUE
                while True:
                    # Get item in DONE_QUEUE. If DONE_QUEUE is empty, it'll raise an Empty Exception
                    item = DONE_QUEUE.get(False)
                    if item and item["request"]["func"] is add_one:
                        item["request"]["args"][0] = item["result"]
            except Empty:
                # No needs to logs, maybe there is no task ...
                # logging.warning("Failed to complete tick in time! Skipping rest of tick.")
                pass
            # Log messages from other process
            try:
                while True:
                    # Get item in LOGGING_QUEUE. If LOGGING_QUEUE is empty, it'll raise an Empty Exception
                    item = LOGGING_QUEUE.get(False)
                    if item:
                        message = "Thread #%s: %s" % (item['id'], item['message'])
                        if item['type'] == 'debug':
                            logging.debug(message)
                        elif item['type'] == 'info':
                            logging.info(message)
                        elif item['type'] == 'warn':
                            logging.warning(message)  # logging.warn is depracated, please use logging.warning
                        elif item['type'] == 'error':
                            logging.error(message)
                        elif item['type'] == 'exception':
                            logging.exception(message, item['exception'])
            except Empty:
                pass
            # Wait for a specific amount of time if needed
            need_to_finish_in = finish_tick_at - time.time()
            if need_to_finish_in > 0:
                # logging.debug("Waiting for %.2f ms" % need_to_finish_in)
                time.sleep(need_to_finish_in)

            tick += 1
    except KeyboardInterrupt:
        pass
    logging.info("Shutting server down!")
    if reactor.running:
        reactor.stop()
    for _ in workers:
        TASK_QUEUE.put(None)
        del _  # Gotta save memory, but I guess not when it's shutting down
    time.sleep(2)  # Waits for all workers to shut down (there's gotta be a better way)
    logging.info("Server stopped: goodbye!")
    sys.exit(0)


def _launch_test():
    import pytest

    pytest.main(["-x", "test"])
    pass


def _launch_server():
    try:
        logging.info("Trying to initialize the Blackfire probe")
        # noinspection PyUnresolvedReferences
        from blackfire import probe  # Profiler: https://blackfire.io free with the Git Student Package
    except ImportError:
        BLACKFIRE_ENABLED = False
        logging.info("Blackfire not installed: passing")
    else:
        BLACKFIRE_ENABLED = True
        probe.initialize()
        probe.enable()
        logging.info("Enabled!")

    logging.info("Starting queues...")
    # TODO Find a way to remove it
    global TASK_LIST, TASK_QUEUE, DONE_QUEUE, REQUEST_QUEUE, LOGGING_QUEUE, LOGGING_INFO
    TASK_LIST = {}
    try:
        TASK_QUEUE = multiprocessing.Queue(100)  # Allow the task queue to have up to 100 items in it at any given time
    except ImportError:
        logging.fatal("No available shared semaphore implementation on the host system! See "
                      "https://bugs.python.org/issue3770 for more info.")  # click the bug link
        sys.exit(-1)
    DONE_QUEUE = multiprocessing.Queue(1000)                # Allow the done queue to have up to 1,000 items in it at any given time
    REQUEST_QUEUE = multiprocessing.Queue(1000)             # Queue for items that have a pending request to be executed
    LOGGING_QUEUE = multiprocessing.Queue(1000)             # Queue for logging
    LOGGING_INFO = {"threadName": "Main", "threadId": "0"}  # Currently unused
    logging.info("Started queues!")

    # Fundamental MC constants
    main()
    if BLACKFIRE_ENABLED:
        probe.end()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug",              # Command line flag to set logging in DEBUG mode
                        action="store_true",   # Syntactic sugar to say 'default:"false"'
                        help="set logging to DEBUG level")
    parser.add_argument("--test",               # Only launch tests
                        action="store_true",   # Syntactic sugar to say 'default:"false"'
                        help="Do not launch the server, only launch tests")

    parsedArgs = parser.parse_args()
    debug = parsedArgs.debug
    test = parsedArgs.test

    if debug:
        print('Debug mode enabled. Don\'t forget to remove debug flag for maximum performance !')
    logging_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s")
    logging.root.setLevel(logging_level)

    # Import all classes before importing the main method
    print("Importing classes, please wait ...")
    import classes
    print("Classes imported !")

    if test:
        _launch_test()
    else:
        _launch_server()
