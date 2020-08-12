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

from quarry.net import server
from twisted.internet import reactor

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
    # probe.enable()
    logging.info("Enabled!")

if not sys.version_info.minor >= 8 and sys.version_info.major >= 3:
    logging.fatal("McPy needs Python version 3.8.0 or higher to run!")
    sys.exit(-2)

logging.info("Starting queues...")
TASK_LIST = {}
try:
    TASK_QUEUE = multiprocessing.Queue(100)  # Allow the task queue to have up to 100 items in it at any
    # given time
except ImportError:
    logging.fatal("No available shared semaphore implementation on the host system! See "
                  "https://bugs.python.org/issue3770 for more info.")  # click the bug link
    sys.exit(-1)
DONE_QUEUE = multiprocessing.Queue(1000)  # Allow the done queue to have up to 1,000 items in it at any given time
REQUEST_QUEUE = multiprocessing.Queue(1000)  # Queue for items that have a pending request to be executed
LOGGING_INFO = {"threadName": "Main", "threadId": "0"}  # Currently unused
logging.info("Started queues!")

# Fundamental MC constants
totalTime = 0  # Time since the world was created in ticks
dayTime = 0    # Time of day in ticks
players = []   # Number of players online


def send_task(func, args: list, kwargs: dict, dataOut: multiprocessing.Queue, taskId: int) -> [int, None]:
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


def worker(inQueue: multiprocessing.Queue, outQueue: multiprocessing.Queue, workerId: str):
    logging.info("Worker ID {0} has started up.".format(workerId))
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
        except Exception as e:
            logging.warning("Error in thread ID {0}: {1}".format(workerId, str(e)))
            result = "error"  # idk the best way to define a error result
        outQueue.put({"request": item, "result": result})
    logging.info("Worker ID {0} has completed all tasks.".format(workerId))


def networker(factory, _reactor):
    listener = ("0.0.0.0", 25565)
    try:
        factory.listen(*listener)
        logging.info("Startup done! Listening on {0[0]}:{0[1]}".format(listener))
        _reactor.run()
    except Exception as e:
        logging.exception("Exception in networking thread! Restarting... {0}".format(str(e)))
        time.sleep(5)
        networker(factory, _reactor)


def main():
    logging.info("Trying to find number of available cores")
    try:
        avaliCPUs = len(os.sched_getaffinity(0))
    except AttributeError:
        # Fix for windows, which doesnt support getaffinity
        logging.warning(
            "Falling back to multiprocessing cpu_count to calc cores. Most likely getaffinity is not supported on "
            "your OS")
        avaliCPUs = multiprocessing.cpu_count()

    if avaliCPUs < 2:
        avaliCPUs = 2  # Force at least 2 workers, just in case only one core is available: one worker to do all the
        # major tasks and one to just take care of networking: THIS WILL BE LAGGY: VERY LAGGY
    logging.info("Found {0} cores available!".format(avaliCPUs))
    workers = []
    for _ in range(avaliCPUs - 1):  # Reserve one worker for the networking thread
        del _
        workerId = str(round(random.random() * 100000))
        logging.info("Starting worker ID {0}".format(workerId))
        funcArgs = (TASK_QUEUE, DONE_QUEUE, workerId)
        p = multiprocessing.Process(target=worker, args=funcArgs)
        p.start()
        logging.info("Started worker.")
        workers.append(p)
    factory = ChatRoomFactory()
    factory.motd = "Chat Room"
    logging.info("Starting networking worker")
    networkingProcess = multiprocessing.Process(target=networker, args=(factory, reactor))
    networkingProcess.start()
    logging.info("Started worker.")
    try:
        while True:
            taskIds = []
            startTickAt = time.time()
            finishTickAt = startTickAt + 0.05  # add 50 milliseconds or one tick
            taskIds, tid = returnTaskId(taskIds)
            send_task(addOne, [totalTime], {}, DONE_QUEUE, tid)
            taskIds, tid = returnTaskId(taskIds)
            send_task(addOne, [dayTime], {}, DONE_QUEUE, tid)
            needToFinishIn = abs(finishTickAt - time.time())
            try:
                # noinspection PyArgumentEqualDefault
                for item in DONE_QUEUE.get(True, needToFinishIn):
                    for _ in item:
                        if item["request"]["func"] is addOne:
                            item["request"]["args"][0] = item["result"]
            except Empty:
                logging.warning("Failed to complete tick in time! Skipping rest of tick.")
    except KeyboardInterrupt:
        logging.info("Shutting server down!")
        reactor.stop()
        for _ in workers:
            TASK_QUEUE.put(None)
            del _  # Gotta save memory, but I guess not when it's shutting down
        time.sleep(2)  # Waits for all workers to shut down (there's gotta be a better way)
        logging.info("Server stopped: goodbye!")

if __name__ == '__main__':
    main()
if BLACKFIRE_ENABLED:
    probe.end()

