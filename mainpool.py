import asyncio
import json
from time import time
from typing import List
from datetime import datetime

import channels.channels as channels
import globals
from channels.channelbase import ChannelsBase
from consts import Consts
from exchangeserver import ExchangeServer
from logger import logger
from mutualcls import SubscriptChannelArg
from sourcepool import SourcePool


class MainPool():
    def __init__(self,  loop:asyncio.AbstractEventLoop, 
                        source_pool:SourcePool|None, 
                        channel_base:ChannelsBase,
                        exchange_server1:ExchangeServer|None=None,
                        exchange_bindings1:dict=None,
                        exchange_server2:ExchangeServer|None=None,
                        exchange_bindings2:dict=None,
                        ):
        '''
        sources: source Module to read
            [{'id':'module_id(str)','type':'ModbusTcp','ip':'192.168.1.99','port':'502','unit':0x1, 'address':51, 'regNumber':2, 'function':4, 'period':0.5},...]
        channeBlase: channe Blase
        MBServAddrMap: ModBus server address map for requesting node data
            [{'unit':0x1, 'map':{
                        'di':[{'id':4207,'addr':1,'len':2},{'id':4208,'addr':3,'len':5},.......],
                        'hr':[{'id':4209,'addr':0,'type':'int'},{'id':4210,'addr':1,'type':'float'},..........] }  }]
        '''
        self.loop = loop
        self.cancelEvent=asyncio.Event()
        self.source_pool=source_pool
        self.channel_base=channel_base
        if source_pool:       
            self.source_pool.readAllOneTime()                    #TODO  проверить как работает если нет доступа к source
                                                                #       или заполнять Null чтобы первый раз сработало по изменению
            for node in (channel for channel in self.channel_base.channels if isinstance(channel,channels.Node)):
                for source in self.source_pool.sources:
                    if source.id==node.sourceId:
                        node.source=source
                        break
        self.exchange_server1=exchange_server1
        self.exchange_bindings1 =exchange_bindings1 if exchange_bindings1!=None else {}
        self.exchange_server2=exchange_server2
        self.exchange_bindings2 =exchange_bindings2 if exchange_bindings2!=None else {}
        self.set_tasks()
            
    
    def start(self):   
        if self.exchange_server1:
            self.exchange_server1.start() 
        if self.exchange_server2:
            self.exchange_server2.start() 
        self.start_loop()

    def start_loop(self):
        try:
            logger.info ('start main loop')
            self.loop.run_forever()
            print ('stop main loop')
        except KeyboardInterrupt:
            logger.info ('************* KeyboardInterrupt *******************')
            self.cancelEvent.set()
            for task in asyncio.all_tasks(loop=self.loop):
                print(f'Task {task.get_name()} cancelled')
                task.cancel()
            
        finally:
            self.loop.run_until_complete(self.source_pool.close_sources())
            self.loop.stop()
            print ('************* main loop close *******************')

    def set_tasks(self):
            self.loop.create_task(self.calc_channel_base_loop(), name='reader')
    
    async def calc_channel_base_loop(self): 
        while True:
            before=time()
            for channel in self.channel_base.channels:                          #calc Channels
                channel()
                # print(f'id:{channel.id}={channel.result}')

                                
            for channelId, binding in self.exchange_bindings1.items():           #set vaues for Modbus Excange Server 1
                self.exchange_server1.setValue(channelId, binding.value)
            for channelId, binding in self.exchange_bindings2.items():           #set vaues for Modbus Excange Server 2
                self.exchange_server2.setValue(channelId, binding.value)
            

            delay=globals.CHANNELBASE_CALC_PERIOD-(time()-before)
            if delay<=0:
                logger.warning(f'Not enough time for channels calc loop, {len(self.channel_base.channels)} channels ')
            await asyncio.sleep(delay)

        
