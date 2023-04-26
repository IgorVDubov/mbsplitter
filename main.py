#!/usr/bin/env python

import asyncio
import sys

from gather.mylib import logger as loggerLib
from loguru import logger

if sys.platform == 'win32':                 # Если запускаем из под win   
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())   


import modbusconfig as mb_config

from gather.sourcepool import SourcePool
from gather.interfaces.modbus_server.server import MBServer
from gather.mainloop import MainLoop


def init():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if len(modules := mb_config.module_list):
        source_pool = SourcePool(modules, loop)
    else:
        raise Exception('No source modules in modbusconfig!') 
    modbus_exchange_server_1 = MBServer(
                            source_pool.sources,
                            mb_config.modbus_server_1['host'],
                            mb_config.modbus_server_1['port'])
    modbus_exchange_server_2 = MBServer(
                            source_pool.sources,
                            mb_config.modbus_server_2['host'],
                            mb_config.modbus_server_2['port'])
    
    print('Sources')
    print(source_pool)
    print(f'Modbus Exchange Server1: {mb_config.modbus_server_1["host"]}:{mb_config.modbus_server_1["port"]}')
    print(f'Modbus Exchange Server2: {mb_config.modbus_server_2["host"]}:{mb_config.modbus_server_2["port"]}')
    
    main_loop = MainLoop(loop, 
                         source_pool, 
                         modbus_exchange_server_1,
                         modbus_exchange_server_2,
                         0.5)
    logger.info('init done')
    return main_loop

def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    main_loop = init()
    main_loop.start()

if __name__=='__main__':
    main()
    # test_component()
    