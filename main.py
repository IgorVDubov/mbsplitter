#!/usr/bin/env python

import asyncio
import sys

from gather.mylib import logger as loggerLib
from loguru import logger

if sys.platform == 'win32':                 # Если запускаем из под win
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


import modbusconfig as mb_config

from gather.sourcepool import SourcePool
from gather.interfaces.modbus_server.server import MBServer, mb_server_init
from gather.mainloop import MainLoop
from gather.myexceptions import ConfigException


def init():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if len(modules := mb_config.source_list):
        source_pool = SourcePool(modules, mb_config.POLL_PERIOD, loop)
    else:
        raise ConfigException('No source modules in modbusconfig!')
    modbus_exchange_server_1 = loop.run_until_complete(mb_server_init(
        source_pool.sources,
        mb_config.modbus_server_1['host'],
        mb_config.modbus_server_1['port'],
        loop=loop))
    modbus_exchange_server_2 = loop.run_until_complete(mb_server_init(
        source_pool.sources,
        mb_config.modbus_server_2['host'],
        mb_config.modbus_server_2['port'],
        loop=loop))

    print('Sources')
    print(source_pool)
    print(f'Modbus Exchange Server1: {mb_config.modbus_server_1["host"]}\
                                        :{mb_config.modbus_server_1["port"]}')
    print(f'Modbus Exchange Server2: {mb_config.modbus_server_2["host"]}\
                                        :{mb_config.modbus_server_2["port"]}')

    main_loop = MainLoop(loop,
                         source_pool,
                         modbus_exchange_server_1,
                         modbus_exchange_server_2,
                         mb_config.POLL_PERIOD)
    logger.info('init done')
    return main_loop


def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    main_loop = init()
    main_loop.start()


if __name__ == '__main__':
    main()
    # test_component()
