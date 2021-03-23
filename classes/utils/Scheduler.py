import logging
from queue import PriorityQueue
import threading

import classes.Server as Server

from ..utils.Thread import AtomicInteger


class Scheduler():

    def __init__(self, id, tick, func, **args):
        self.id = id
        self.tick = tick
        self.func = func
        self.args = args

    def __lt__(self, other):
        """
        Used for comparator for PriorityQueue
        """
        if self.tick < other.tick:
            return True
        elif self.tick > other.tick:
            return False
        return self.id <= other.id


class SchedulerManager():

    def __init__(self, server: Server, current_tick=0):
        self.server = server
        self.current_tick = current_tick
        self.atomic_id = AtomicInteger()
        self.pending = PriorityQueue()
        self._lock = threading.Lock()

    def tick(self, current_tick):
        self.current_tick = current_tick
        while not self.pending.empty():
            task = self.pending.get(False)
            # Check if we have to run function now or later
            if task.tick <= current_tick:
                # Run function
                try:
                    task.func(self.server, **task.args)
                except Exception:
                    logging.exception('Exception while running task %d', task.id)
            else:
                # Put back this task in the queue
                self.add_pending(task)
                # Exit the loop
                break

    def _add_pending(self, scheduler):
        with self._lock:
            self.pending.put_nowait(scheduler)

    def schedule(self, func, **args):
        self.schedule_after(1, func, **args)

    def schedule_after(self, after, func, **args):
        if after <= 0:
            after = 1
        scheduler_id = self.atomic_id.get_and_increment()
        scheduler = Scheduler(scheduler_id, self.current_tick + after, func, **args)
        self._add_pending(scheduler)

    def schedule_repeating(self, after, repeat, func, **args):
        if after <= 0:
            after = 1
        id = self.atomic_id.get_and_increment()
        # TODO
