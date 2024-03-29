import asyncio
from time import time
from typing import TypedDict

from .consts import SourceTypes, Formats
from .interfaces.modbus_client.aclient import AsyncModbusClient, ABaseModbusClient
from .interfaces.modbus_client.connection import AModbusConnection
from loguru import logger
from . import myexceptions
from .mutualcls import NewID




class Source:
    id: int
    period: float
    result: list
    addr_pool: Formats.CO | Formats.DI | Formats.HR | Formats.IR

    def __init__(self, module: dict, exist_clients: list[ABaseModbusClient | None]):
        try:
            self.id = NewID()
            
            self.result = None
            self.addr_pool = module.get('addr_pool')
            if module['type'] == SourceTypes.MODBUS_TCP:
                use_exist_client = False
                for client in exist_clients:
                    # TODO если будут использоваться НЕ только TCP клиенты поменять алгоритм поиска существующего клиента
                    if module['ip'] == client.ip and module['port'] == client.port:
                        new_client = client
                        use_exist_client = True
                        break
                if not use_exist_client:
                    new_client = AsyncModbusClient(
                        module['ip'], module['port'])
                self.connection = AModbusConnection(new_client,
                                                    self.addr_pool,
                                                    module['address'],
                                                    module['count'],
                                                    module['unit'],
                                                    module.get('map_unit'),
                                                    module.get('map_address')
                                                    )
            else:
                raise myexceptions.ConfigException(
                    f'No implementation for type {module["type"]}')
        except KeyError:
            raise myexceptions.ConfigException(
                f'Not enoth data fields in mopdule config srting {module}')

    @property
    def connected(self):
        return self.connection.connected
    
    async def start(self):
        if not self.connection.connected:
            await self.connection.start()
    
    async def close(self):
        if self.connection.connected:
            await self.connection.close()

    async def read(self):
        try:
            self.dost = self.connection.connected
            self.result = await self.connection.read()
        except myexceptions.SourceException as e:
            self.error = e
            self.result = None
        except Exception as e:
            logger.error(f'[Source][read] exception {e}')
            raise e
        return self.result
    
    async def write(self, value):
        await self.connection.writeRegister(value)

    def get_client(self):
        return self.connection.client
    
    def __str__(self):
        return f' {id(self)}    id:{self.id}, conn_id:{id(self.connection.client)} {self.connection}'

class ClientSrcIndex(TypedDict):
    client: AsyncModbusClient
    source: list[Source]

async def init_source(module, clients):
    source =   Source(module, clients)
    await asyncio.sleep(0)
    return source

class SourcePool(object):
    clients: list[ABaseModbusClient]
    sources: list[Source]
    loop: asyncio.AbstractEventLoop
    reader_tasks: list[asyncio.Task]
    clients_sources: ClientSrcIndex
    
    def __init__(self, modules, period, loop: asyncio.AbstractEventLoop=None):
        self.clients = []
        self.sources = []
        self.reader_tasks = []
        self.clients_sources = {}
        # self.results=[]
        for module in modules:
            # source =  loop.run_until_complete(Source(module, self.clients))
            source = loop.run_until_complete(init_source(module, self.clients))
            client = source.get_client()
            if client and client not in self.clients:
                self.clients.append(client)
                self.clients_sources[client]=[]
            self.clients_sources[client].append(source)
            self.sources.append(source)
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        if self.loop.is_running():
            self.loop.create_task(self.start_source_clients())
        else:
            self.loop.run_until_complete(self.start_source_clients())
        self.set_tasks(period)

    async def start_source_clients(self):
        for client in self.clients:
            logger.info(f'start Sourse client {client}')
            self.loop.create_task(client.start())

    async def close_sources(self):
        for client in self.clients:
            client.close()
            await asyncio.sleep(0)

    async def stop(self):
        logger.info('get stop signal, stopping tasks:')
        for task in self.reader_tasks:
            result=task.cancel()
            logger.info(f'stop task {task.get_name()} -> {result}')
        logger.info('get stop signal, stopping connection clients:')
        for client in self.clients:
            if client.connected:
                await client.close()
            logger.info(f'stop client {client}')
        
            
    def str_clients(self):
        s = ''
        for client in self.clients:
            s += f'{id(client)}  {client}'+'\n'
        return s[:-1]

    def __str__(self):
        s = ''
        for source in self.sources:
            s += str(source)+'\n'
        return s[:-1]
    
    def set_tasks(self, period):
        for client in self.clients_sources.keys():
            self.loop.create_task(self.client_reader(
                client, period), name='client_reader_'+str(id(client)))
    
    async def client_reader(self, client, period):
        logger.debug(
            f'start source_reader client:{client.ip}')
        while True:
            try:
                before = time()
                for source in self.clients_sources[client]:
                    # async with asyncio.timeout(period):
                    await asyncio.gather(source.read())
                    #  await asyncio.gather(source.read())
                # await asyncio.gather(*(source.update() for source in self.clients_sources[client]))
                await asyncio.sleep(0)
                delay =period - (time() - before)
                if delay <= 0:
                    logger.warning(
                        f'Not enough time for source read, client id:{client.ip}, delay={delay}')
                        # f'Not enough time for source read, source id:{source.id}, delay={delay}')
                    delay = 0
                await asyncio.sleep(delay)
            except TimeoutError as ex:
                logger.warning(
                    f"TimeoutError for {client.ip}:{client.port} reading \
                        addr{source.connection.address} \
                            unti:{source.connection.unit}", ex)
            except asyncio.CancelledError:
                logger.warning(
                    f"Got CancelledError close \
                        client connection {client.ip}:{client.port}")
                # if client.connected:
                #     client.close()
                #break
        logger.info(
                    f"reader stopped  {client.ip}:{client.port}")

    def readAllOneTime(self):
        for source in self.sources:
            # print(f'run read task {source.id}')
            self.loop.run_until_complete(source.read())
            # print(f'next step  after read task {source.result}')
            if not source.result:
                logger.error(f'!!!!!!!!!!!!!!! Cant read source {source.id}')

        # Let also finish all running tasks:
        # pending = asyncio.Task.all_tasks()
        # self.loop.run_until_complete(asyncio.gather(*pending))
