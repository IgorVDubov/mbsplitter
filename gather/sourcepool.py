import asyncio
from time import time

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
            self.period = module.get('period')
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
        return self.result
    
    async def write(self, value):
        await self.connection.writeRegister(value)

    def get_client(self):
        return self.connection.client
    
    def __str__(self):
        return f' {id(self)}    id:{self.id}, period:{self.period}s, conn_id:{id(self.connection.client)} {self.connection}'


class SourcePool(object):
    clients: list[ABaseModbusClient]
    sources: list[Source]
    loop: asyncio.AbstractEventLoop
    reader_tasks: list[asyncio.Task]
    
    def __init__(self, modules, loop=None):
        self.clients = []
        self.sources = []
        self.reader_tasks = []
        # self.results=[]
        for module in modules:
            source = Source(module, self.clients)
            client = source.get_client()
            if client and client not in self.clients:
                self.clients.append(client)
            # TODO ????? помещать сюда только если успешный инит клиента и тест чтения по адресу
            self.sources.append(source)
        if loop is None:
            self.loop = asyncio.get_event_loop()
        else:
            self.loop = loop
        if self.loop.is_running():
            self.loop.create_task(self.start_source_clients())
        else:
            self.loop.run_until_complete(self.start_source_clients())
        self.setTasks()

    async def start_source_clients(self):
        for client in self.clients:
            logger.info(f'start Sourse client {client}')
            await client.start()

    async def close_sources(self):
        for client in self.clients:
            await client.close()

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

    def setTasks(self):
        for source in self.sources:
            self.reader_tasks.append(self.loop.create_task(
                                        self.loopSourceReader(
                                                source),
                                                name='SourceReader_'+str(source.id)))

    async def loopSourceReader(self, source: Source):
        logger.debug(
            f'start loopReader client:{source.id}, period:{source.period}')
        while True:
            # try:
                before = time()
                try:
                    self.result = await source.read()
                    # self.result = [1]
                    # print(f'after read {source.id} def result:{self.result} connected={source.connected}')

                except asyncio.exceptions.TimeoutError as ex:
                    print(
                        f"!!!!!!!!!!!!!!!!!!! asyncio.exceptions.TimeoutError for {source.id}:", ex)
                # except ModbusExceptions.ModbusException as ex:                                            #TODO взять exception от клиента
                #     print(f"!!!!!!!!!!!!!!!!!!! ModbusException in looper for {client.id} :",ex)

                delay = source.period-(time()-before)
                if delay <= 0:
                    logger.warning(
                        f'Not enough time for source read, source id:{source.id}, delay={delay}')
                await asyncio.sleep(delay)
            # except asyncio.CancelledError:
            #     print(
            #         f"Got CancelledError close client connection{id(source.connection)}")
            #     if source.connection.connected:
            #         await source.connection.close()
            #     break

    def readAllOneTime(self):
        for source in self.sources:
            # print(f'run read task {source.id}')
            self.loop.run_until_complete(source.read())
            # print(f'next step  after read task {source.result}')
            if not source.result:
                print(f'!!!!!!!!!!!!!!! Cant read source {source.id}')

        # Let also finish all running tasks:
        # pending = asyncio.Task.all_tasks()
        # self.loop.run_until_complete(asyncio.gather(*pending))
