import logging
import multiprocessing
import time
from queue import Full

import classes.Server as Server

from ..Exceptions import ServerException


class MultiProcessing():

    def __init__(self, server: Server, worker_number, max_size=100000):
        self.server = server
        self.worker_number = worker_number
        self.max_size = max_size
        self.started = True
        self.TASK_LIST = multiprocessing.Queue()
        self.workers = []
        for i in range(self.worker_number):
            func_args = (self.TASK_LIST,)
            p = multiprocessing.Process(target=MultiProcessing.worker, args=func_args, name='PROCESS_%d' % (i,))
            self.workers.append(p)

    def start(self):
        self.started = True
        for p in self.workers:
            logging.info('Starting worker %s', p.name)
            p.start()
        logging.info('Workers started !')

    def stop(self, timeout=0):
        self.started = False
        if timeout < 0:
            timeout = 0
        # Sleep & then terminate processes
        start = time.time()
        logging.info('Waiting for process to end ...')
        while time.time() - start >= timeout:
            if not any(p.is_alive() for p in self.workers):
                break
            time.sleep(0.1)
        for p in self.workers:
            p.terminate()
        logging.info('Process stopped !')

    def get_worker(self, id):
        return self.workers[str(id)]

    def add_task(self, func, args: list, **kwargs):
        if not self.started:
            raise ServerException('Cannot add tasks while server is not started')
        data = {
            'func': func,
            'args': args,
            'kwargs': kwargs,
        }
        try:
            self.TASK_LIST.put_nowait(data)
        except Full:
            logging.warning()

    @staticmethod
    def worker(in_queue: multiprocessing.Queue):
        while True:
            try:
                item = in_queue.get()
            except KeyboardInterrupt:
                break
            if item is None:
                break
            func = item['func']
            args = item['args']
            kwargs = item['kwargs']
            # Call the function
            try:
                func(*args, **kwargs)
            except Exception:
                logging.exception('Exception while running task %s (args = %s, kwargs = %s)', func, args, kwargs)
