#!/usr/bin/env python3

import asyncio
import os.path
import sys
from typing import List

from loguru import logger

import logger as loggerLib

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  #Если запускаем из под win    

import importlib

import globals

from splitter import scadaconfig as scada_config
import channels.channels
from channels.channelbase import channel_base_init
from exchangeserver import MBServerAdrMapInit, ModbusExchangeServer
from mainpool import MainPool
from mutualcls import (ChannelSubscriptionsList, Data, EList,
                       SubscriptChannelArg, WSClient)
from sourcepool import SourcePool


def init():
    loop=asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if len(modules:=scada_config.module_list):
        sourcePool=SourcePool(modules,loop)
    else:
        sourcePool=None 
    dbQuie=None
    channel_base=channel_base_init(scada_config.channels_config, dbQuie)
    newAddrMap1, exchangeBindings1 = MBServerAdrMapInit(channel_base,scada_config.mb_server1_addr_map)
    newAddrMap2, exchangeBindings2 = MBServerAdrMapInit(channel_base,scada_config.mb_server2_addr_map)
    ModbusExchServer1=ModbusExchangeServer(newAddrMap1, globals.MBServer1_params['host'], globals.MBServer1_params['port'],loop=loop)
    ModbusExchServer2=ModbusExchangeServer(newAddrMap2, globals.MBServer2_params['host'], globals.MBServer2_params['port'],loop=loop)
    print ('Source clients')
    print (sourcePool.str_clients())
    print ('Sources')
    print (sourcePool)
    print(f'Modbus Exchange Server 1: {globals.MBServer1_params["host"]}, {globals.MBServer1_params["port"]}')
    print('ExchangeBindings 1 ')
    print(exchangeBindings1)
    print(f'Modbus Exchange Server 2: {globals.MBServer2_params["host"]}, {globals.MBServer2_params["port"]}')
    print('ExchangeBindings 2')
    print(exchangeBindings2)
    
    mainPool=MainPool(loop, sourcePool, channel_base, ModbusExchServer1, exchangeBindings1, ModbusExchServer2, exchangeBindings2)
    logger.info ('init done')
    return mainPool


def main():
    loggerLib.loggerInit('ERROR')
    logger.info('Starting........')
    mainPool=init()
    mainPool.start()
    

if __name__=='__main__':
    main()
    # test_component()
    