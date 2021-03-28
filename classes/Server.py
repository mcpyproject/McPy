import logging
import time
from twisted.internet import reactor

from .mcPy.MultiProcessing import MultiProcessing
from .mcPy.Parser import Parser
from .entity.Entity import EntityManager
from .network.Connection import NetworkController
from .network.PacketType import PacketType
from .player.Player import PlayerManager
from .utils.Scheduler import SchedulerManager

class Server:
    entity_manager: EntityManager
    multi_processing: MultiProcessing
    scheduler_manager: SchedulerManager
    player_manager: PlayerManager

    def __init__(self, parser: Parser, avail_cores=2):
        logging.info("%d cores available", avail_cores)
        self.parser = parser
        if avail_cores < 2:
            avail_cores = 2
        self.avail_cores = avail_cores
        self._tick = 0
        self.started = False
        self.entity_manager = EntityManager(self)
        # Reserve one core for the network stuff
        self.multi_processing = MultiProcessing(self, avail_cores - 1)
        self.scheduler_manager = SchedulerManager(self)
        self.player_manager = PlayerManager(self)

    def start(self, host, port):
        if self.started:
            return
        logging.info('Launching server ...')
        self.started = True
        logging.info('Launching processes ...')
        self.multi_processing.start()
        NetworkController.start_process(self, host, port)

        # TODO Move next lines in another place
        self.total_time = 0
        self.day_time = 0
        logging.info('McPy started on %s:%s', host, port)
        self.start_internal_tick()

    def start_internal_tick(self):
        logging.info('Starting ticks')
        while self.started:
            start_tick_at = time.time()
            finish_tick_at = start_tick_at + 0.05  # Add 50ms or one tick
            # Tick
            try:
                self.tick()
            except KeyboardInterrupt:
                logging.info('Tick: Got KeyboardInterrupt, interrupting loop')
                break
            # Check if we need to wait until next tick
            need_to_finish_in = finish_tick_at - time.time()
            if need_to_finish_in > 0:
                # Wait until next tick
                try:
                    time.sleep(need_to_finish_in)
                except KeyboardInterrupt:
                    logging.info('Tick: Got KeyboardInterrupt, interrupting loop')
                    break

    def tick(self):
        """
        Called on every ticks
        This method will call every components that is tickable
        """
        self._tick += 1
        current_tick = self._tick
        # Tick common classes
        # Execute SchedulerManager before other classes
        self.scheduler_manager.tick(current_tick)
        self.entity_manager.tick(current_tick)
        # Handle incoming packets
        NetworkController.tick(current_tick)
        # TODO Move next lines in another place
        self.total_time += 1
        self.day_time += 1
        self.day_time %= 24000
        # Update time
        NetworkController.send_packet(packet_type=PacketType.TIME_UPDATE, game_time=self.total_time, day_time=self.day_time)

    def run_test(self):
        import pytest
        pytest.main(['-x', 'test'])

    def stop(self):
        logging.info("Stopping server ...")
        self.started = False
        NetworkController.stop_process()
        # Stop multi_processing after 5 seconds
        self.multi_processing.stop(5000)
        self.stop_internal_tick()

        if reactor.running:
            reactor.stop()
        try:
            time.sleep(2)  # Waits for all workers to shut down (there's gotta be a better way)
        except:
            pass

    def stop_internal_tick(self):
        logging.info('Stopping ticks')
