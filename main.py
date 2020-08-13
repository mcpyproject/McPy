# coding=utf-8
# Import general libraries
import gc
import logging
import multiprocessing
import os
import random
import sys
import time
from queue import Empty, Full  # multiprocessing.Queue() full and empty exceptions

# Check if current python version is 3.8
if sys.version_info < (3, 8):
    logging.fatal('McPy needs Python version 3.8.0 or higher to run! Current version is %s.%s.%s' % (sys.version_info.major, sys.version_info.minor, sys.version_info.micro))
    sys.exit(-2)

from quarry.net import server
from twisted.internet import reactor


def send_task(func, args: list, kwargs: dict, dataIn: multiprocessing.Queue, taskId: int) -> [int, None]:
    taskData = {
        'func': func,
        'args': args,
        'kwargs': kwargs
    }
    try:
        td = taskData
        td["id"] = taskId
        dataIn.put_nowait(taskData)  # If queue is full, throw queue.Full exception
    except Full:
        logging.warning("Queue {0} is full!".format(dataIn.__name__))
        return 1
    TASK_LIST[taskId] = taskData
    return


def get_all_completed_tasks(queueInUse):
    while not queueInUse.empty():  # Not too reliable, so also double check and handle the Empty exception
        try:
            yield queueInUse.get(False)
        except Empty:
            break


def addOne(a):
    return a + 1


def getRandTaskId() -> int:
    taskId = round(random.random() * 10000000)  # Generate a random ID for the task
    return taskId


def returnTaskId(taskIdList: list, taskId: int = None):
    if not taskId:
        taskId = getRandTaskId()
    taskIdList.append(taskId)
    return taskIdList, taskId


# The next two classes are from https://quarry.readthedocs.io
class ChatRoomProtocol(server.ServerProtocol):

    def __init__(self):
        self.request_item_queue = REQUEST_QUEUE

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

    def __init__(self):
        self.protocol = ChatRoomProtocol
        self.motd = "Chat Room Server"  # Later customizable

    def send_chat(self, message):
        for player in self.players:
            player.send_packet("chat_message", player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0))


def log(loggingQueue: multiprocessing.Queue, message, id, type = "info", exception=None):
    loggingQueue.put({
        "type": type,
        "id": str(id),
        "message": message,
        "exception": exception
    })


def worker(inQueue: multiprocessing.Queue, outQueue: multiprocessing.Queue, loggingQueue: multiprocessing.Queue, workerId: str):
    log(loggingQueue, "Worker started up.", workerId)
    while True:
        try:
            item = inQueue.get()  # Waits for a new item to appear on the queue
        except KeyboardInterrupt:
            outQueue.put(None)
            break
        if item is None:  # Sending None down the pipe stops the first worker that grabs it: send it as many times as
            # there are workers and they'll all stop: this is how McPy shuts all of them down safely
            outQueue.put(None)
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
            log(loggingQueue, "Exception in Thread", workerId, type="exception", exception=ex)
            result = "error"  # idk the best way to define a error result
        outQueue.put({
            "request": item,
            "result": result
        })
    log(loggingQueue, "Tasks completed", workerId)


def networker(factory, _reactor, loggingQueue: multiprocessing.Queue):
    listener = ("0.0.0.0", 25565)
    try:
        factory.listen(*listener)
        log(loggingQueue, "Startup done! Listening on {0[0]}:{0[1]}".format(listener), "Networker")
        _reactor.run()
    except Exception as ex:
        log(loggingQueue, "Exception in networking thread! Restarting...", "Networker", type="exception", exception=ex)
        time.sleep(5)
        networker(factory, _reactor, logging)


def main():
    # Here start the server :D
    logging.info("Trying to find number of available cores")
    try:
        availCPUs = len(os.sched_getaffinity(0))
    except AttributeError:
        # Fix for windows, which doesnt support getaffinity
        logging.warning(
            "Falling back to multiprocessing cpu_count to calc cores. Most likely getaffinity is not supported on "
            "your OS")
        availCPUs = multiprocessing.cpu_count()

    if availCPUs < 2:
        availCPUs = 2  # Force at least 2 workers, just in case only one core is available: one worker to do all the
        # major tasks and one to just take care of networking: THIS WILL BE LAGGY: VERY LAGGY
    logging.info("Found {0} cores available!".format(availCPUs))
    workers = []
    for _ in range(availCPUs - 1):  # Reserve one worker for the networking thread
        del _
        workerId = str(round(random.random() * 100000))
        logging.info("Starting worker ID {0}".format(workerId))
        funcArgs = (TASK_QUEUE, DONE_QUEUE, LOGGING_QUEUE, workerId)
        p = multiprocessing.Process(target=worker, args=funcArgs)
        p.start()
        logging.info("Started worker.")
        workers.append(p)
    factory = ChatRoomFactory()
    factory.motd = "Chat Room"
    logging.info("Starting networking worker")
    funcArgs = (factory, reactor, LOGGING_QUEUE)
    networkingProcess = multiprocessing.Process(target=networker, args=funcArgs)
    networkingProcess.start()
    logging.info("Started worker.")
    try:
        tick = 0
        while True:
            # print("Tick = %d" % tick)
            taskIds = []
            startTickAt = time.time()
            finishTickAt = startTickAt + 0.05 # add 50 milliseconds or one tick
            # TODO The next 4 lines are here only for TESTING, don't forget to remove these in the futur (and to move it to another place, like inside World.tick function)
            taskIds, tid = returnTaskId(taskIds)
            send_task(addOne, [totalTime], {}, TASK_QUEUE, tid)
            taskIds, tid = returnTaskId(taskIds)
            send_task(addOne, [dayTime], {}, TASK_QUEUE, tid)
            try:
                # noinspection PyArgumentEqualDefault
                # The goal here is to loop over each element in DONE_QUEUE
                while True:
                    # Get item in DONE_QUEUE. If DONE_QUEUE is empty, it'll raise an Empty Exception
                    item = DONE_QUEUE.get(False)
                    if item and item["request"]["func"] is addOne:
                        item["request"]["args"][0] = item["result"]
            except Empty:
                # No needs to logs, maybe there is no task ...
                #logging.warning("Failed to complete tick in time! Skipping rest of tick.")
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
                            logging.warn(message)
                        elif item['type'] == 'error':
                            logging.error(message)
                        elif item['type'] == 'exception':
                            logging.exception(message, item['exception'])
            except Empty:
                pass
            # Wait for a specific amount of time if needed
            needToFinishIn = finishTickAt - time.time()
            if needToFinishIn > 0:
                #logging.debug("Waiting for %.2f ms" % needToFinishIn)
                time.sleep(needToFinishIn)

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

if __name__ == '__main__':
    # Import all classes before importing the main method
    print("Importing classes, please wait ...")
    #import classes
    print("Classes imported !")

    # TODO Use --debug flag
    logging.basicConfig(format="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s", level=logging.DEBUG)
    logging.root.setLevel(logging.NOTSET)

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
        #probe.enable()
        logging.info("Enabled!")

    logging.info("Starting queues...")
    TASK_LIST = {}
    try:
        TASK_QUEUE = multiprocessing.Queue(100)  # Allow the task queue to have up to 100 items in it at any
        # given time
    except ImportError:
        logging.fatal("No available shared semaphore implementation on the host system! See "
                    "https://bugs.python.org/issue3770 for more info.")  # click the bug link
        sys.exit(-1)
    DONE_QUEUE = multiprocessing.Queue(1000)    # Allow the done queue to have up to 1,000 items in it at any given time
    REQUEST_QUEUE = multiprocessing.Queue(1000) # Queue for items that have a pending request to be executed
    LOGGING_QUEUE = multiprocessing.Queue(1000) # Queue for logging
    LOGGING_INFO = {"threadName": "Main", "threadId": "0"}  # Currently unused
    logging.info("Started queues!")

    # Fundamental MC constants
    totalTime = 0  # Time since the world was created in ticks
    dayTime = 0    # Time of day in ticks
    players = []   # Number of players online
    main()
    if BLACKFIRE_ENABLED:
        probe.end()
