# coding=utf-8
import sys
import random
import multiprocessing
import logging
from queue import Empty, Full  # multiprocessing.Queue() full and empty exceptions
from twisted.internet import reactor
from quarry.net.server import ServerFactory, ServerProtocol
import os

logging.basicConfig(format="[%(asctime)s - %(levelname)s - %(threadName)s] %(message)s", level=logging.DEBUG)
logging.info("plz work")
sys.exit(1)
# noinspection PyUnreachableCode
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

assert (sys.version_info.minor >= 8 and sys.version_info.major >= 3)
"McPy needs Python version 3.8.0 or higher to run!"

logging.info("Starting queues...")
TASK_LIST = {}
try:
    TASK_QUEUE = multiprocessing.JoinableQueue(100)  # Allow the task queue to have up to 100 items in it at any
    # given time
except ImportError:
    logging.fatal("No available shared semaphore implementation on the host system! See "
                  "https://bugs.python.org/issue3770 for more info.")  # click the bug link
    sys.exit(-1)
DONE_QUEUE = multiprocessing.Queue(1000)  # Allow the done queue to have up to 1,000 items in it at any given time
LOGGING_INFO = {"threadName": "Main", "threadId": "0"}  # Currently unused
logging.info("Started queues!")


def send_task(func, args: list, kwargs: dict, dataOut: multiprocessing.JoinableQueue, d: dict = LOGGING_INFO) -> [int,
                                                                                                                  None]:
    logging.basicConfig(format="[%(asctime)s - %(level)s] %(message)s")
    taskId = round(random.random() * 10000000)  # Generate a random ID for the task
    taskData = dict(function=func, args=args, kwargs=kwargs)
    try:
        td = taskData
        td["id"] = taskId
        dataOut.put_nowait(taskData)  # If queue is full, throw queue.Full exception
    except Full:
        logging.warning("Queue {0} is full!".format(dataOut.__name__))
        return 1
    TASK_LIST[taskId] = taskData
    return


def return_task(taskData, dataIn: multiprocessing.JoinableQueue, dataOut: multiprocessing.Queue):
    dataIn.task_done()
    dataOut.put(taskData)


def get_all_completed_tasks(queueInUse):
    while not queueInUse.empty():  # Not too reliable, so also double check and handle the Empty exception
        try:
            yield queueInUse.get(False)
        except Empty:
            break


# The next two classes are from https://quarry.readthedocs.io
class ChatRoomProtocol(ServerProtocol):
    def player_joined(self):
        # Call super. This switches us to "play" mode, marks the player as
        #   in-game, and does some logging.
        ServerProtocol.player_joined(self)

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

        # Announce player joined
        self.factory.send_chat(u"\u00a7e%s has joined." % self.display_name)

    def player_left(self):
        ServerProtocol.player_left(self)

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
        self.factory.send_chat("<%s> %s" % (self.display_name, p_text))


class ChatRoomFactory(ServerFactory):
    protocol = ChatRoomProtocol
    motd = "Chat Room Server"  # Later customizable

    def send_chat(self, message):
        for player in self.players:
            player.send_packet("chat_message", player.buff_type.pack_chat(message) + player.buff_type.pack('B', 0))


def worker(inQueue: multiprocessing.JoinableQueue, outQueue: multiprocessing.Queue, workerId: str):
    logging.basicConfig(format="[%(asctime)s - %(level)s] %(message)s")
    logging.info("Worker ID {0} has started up.".format(workerId))
    while True:
        item = inQueue.get()  # Waits for a new item to appear on the queue
        if item is None:  # Sending None down the pipe stops the first worker that grabs it: send it as many times as
            # there are workers and they'll all stop: this is how McPy shuts all of them down safely
            inQueue.task_done()
            outQueue.put(None)
            break
        func = item["func"]
        args = item["args"]
        kwargs = item["kwargs"]
        # noinspection PyBroadException
        try:
            func(*args, **kwargs)  # Calls the requested function: MUST NOT BE DEFINED WITH async def
        except Exception as e:
            logging.warning("Error in thread: {0}".format(str(e)))
        inQueue.task_done()
    logging.info("Worker ID {0} has completed all tasks.".format(workerId))


def networker():
    try:
        reactor.run()
    except Exception as e:
        logging.exception("Exception in reactor thread! {0}".format(str(e)))


def main():
    logging.basicConfig(format="[%(asctime)s - %(level)s] %(message)s")
    logging.info("Trying to find number of available cores")
    avaliCPUs = len(os.sched_getaffinity(0))
    if avaliCPUs > 2:
        avaliCPUs = 2  # Force at least 2 workers, just in case only one core is available: one worker to do all the
        # major tasks and one to just take care of networking: THIS WILL BE LAGGY: VERY LAGGY
    logging.info("Found {0} cores available!".format(avaliCPUs))
    workers = []
    for _ in range(avaliCPUs - 1):  # Reserve one worker for the networking thread
        workerId = str(round(random.random() * 100000))
        logging.info("Starting worker ID {0}".format(workerId))
        funcArgs = (TASK_QUEUE, DONE_QUEUE, workerId)
        p = multiprocessing.Process(target=worker, args=funcArgs)
        p.start()
        logging.info("Started worker.")
        workers.append(p)
        del _
    '''
    networkingFunc = networker
    logging.info("Starting networking worker")
    networkingProcess = multiprocessing.Process(target=networkingFunc)
    networkingProcess.run()
    logging.info("Started worker.")
    '''
    try:
        reactor.run()
    except KeyboardInterrupt:
        logging.info("Shutting server down!")
        #networkingProcess.kill()  # There's no good way to stop this other than kill: but it doesn't use any Queues, so
        # this is safe: for now
        for _ in workers:
            TASK_QUEUE.put(None)
            del _  # Gotta save memory, but I guess not when it's shutting down
        TASK_QUEUE.join()  # Waits for all workers to shut down
        logging.info("Server stopped: goodbye!")


if __name__ == "__main__":
    main()
    if BLACKFIRE_ENABLED:
        probe.end()
