import asyncio
from time import time

from . import defaults
from loguru import logger

from gather.interfaces.modbus_server.server import MBServer
from .sourcepool import SourcePool


class MainLoop():
    loop: asyncio.AbstractEventLoop
    source_pool: SourcePool
    exchange_server_1: MBServer
    exchange_server_2: MBServer
    period: float

    def __init__(self,  loop: asyncio.AbstractEventLoop,
                 source_pool: SourcePool,
                 exchange_server_1: MBServer,
                 exchange_server_2: MBServer,
                 period=None):
        '''
        source_pool: source pool
        exchange_server:  ModBus exchange server
        '''
        self.loop = loop
        self.cancelEvent = asyncio.Event()
        self.source_pool = source_pool
        self.exchange_server_1 = exchange_server_1
        self.exchange_server_2 = exchange_server_2
        self.period = period or defaults.CHANNELBASE_CALC_PERIOD
        self.set_tasks()

    def set_tasks(self):
        self.loop.create_task(self.calc_channel_base_loop(), name='reader')

    def start(self):
        self.exchange_server_1.prepare_start_task()
        self.exchange_server_2.prepare_start_task()
        self.start_loop()

    def start_loop(self):
        logger.info('start main loop')
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            logger.info('************* KeyboardInterrupt *******************')
            self.loop.create_task(self.source_pool.stop())
            self.loop.create_task( self.exchange_server_1.stop())
            self.loop.create_task( self.exchange_server_2.stop())
            self.cancelEvent.set()
            
            # for task in asyncio.all_tasks(loop=self.loop):
            #     print(f'Task {task.get_name()} cancelled')
            #     task.cancel()
            logger.info('stop main loop')
            self.loop.stop()
            print('************* main loop close *******************')

    async def calc_channel_base_loop(self):
            while True:
                try:
                    before = time()
                    for source in self.source_pool.sources:
                        result = source.result
                        # print (f'{result=}')
                        if result is None:
                            result = [None]
                        self.exchange_server_1.set_value_by_id(source.id, result)
                        self.exchange_server_2.set_value_by_id(source.id, result)
                    delay = self.period - (time()-before)
                    if delay <= 0:
                        logger.warning(
                            f'Not enough time for sources calc loop, period={delay}')
                    await asyncio.sleep(delay)
                    if self.cancelEvent.is_set():
                        logger.info('break reader loop by calncel event')
                        break
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
