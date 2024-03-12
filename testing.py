import asyncio
from modbusconfig import source_list, modbus_server_1

from gather.interfaces.modbus_client.connection import AModbusConnection
from gather.interfaces.modbus_client.aclient import AsyncModbusClient
from gather.consts import Formats, SourceTypes

async def test_connection(ip, port, addr_pool, addr, count, unit):
    print('AModbusConnection read test')
    client= AsyncModbusClient(ip, port)
    connection = AModbusConnection(client, addr_pool, addr, count, unit)
    await connection.start()
    print(connection)
    print(f'result={await connection.read()}')
    print(f'{connection.error=}')
    await connection.close()

from gather.sourcepool import Source   
async def test_source(module):
    print('source read test')
    clients = [AsyncModbusClient(module['ip'], module['port'])]
    source = Source(module, clients)
    await source.start()
    print(f'result={await source.read()}')
    await source.close()
    
from gather.sourcepool import SourcePool
async def test_source_pool(module):
    print('SourcePool run test')
    sp = SourcePool(module, asyncio.get_running_loop())
    while True:
        try:
            for source in sp.sources:
                print(f'source {source.id}, result:{source.result}')
            await asyncio.sleep(1)
        except (KeyboardInterrupt, asyncio.CancelledError):
            await sp.stop()
            break

from gather.interfaces.modbus_server.server import MBServer

async def call(server):
    i=1
    while True:
        try:
            i+=1
            server.set_value(3, 1, 0, [i,2])
            # server.setValue(4002,i+50)
            # server.setValue(4003,[1])
            # server.setValue(4004,[i%2==True,0,1])
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
async def test_exchange_server(modules, config):
    sources = SourcePool(modules, asyncio.get_running_loop()).sources
    print('test_exchange_server run test')
    server = MBServer(sources, config['host'], config['port'])
    # server.start()
    # server.set_value(3, 1, 0, [777])
    t1= asyncio.get_running_loop().create_task(call(server))
    t2= asyncio.get_running_loop().create_task(server.serve_forever())
    await asyncio.gather(t1, t2)


from gather.interfaces.modbus_server.server import ModBusServer

async def test_ModBusServer(MBServerAdrMap, modules, host, port):
    sources = SourcePool(modules, asyncio.get_running_loop()).sources
    print('test_exchange_server run test')
    server = ModBusServer(MBServerAdrMap, sources, host, port)
    # server.start()
    # server.set_value(3, 1, 0, [777])
    t1= asyncio.get_running_loop().create_task(call(server))
    t2= asyncio.get_running_loop().create_task(server.serve_forever())
    await asyncio.gather(t1, t2)

async def test_pymodbus_server():
    from pymodbus.datastore import (ModbusSequentialDataBlock, ModbusServerContext,
                                ModbusSlaveContext)
    from pymodbus.server.async_io import ModbusTcpServer

if __name__=='__main__':
    module = {'type': SourceTypes.MODBUS_TCP,
                'ip': '127.0.0.1', 'port': 502, 'unit': 0x1,
                'addr_pool': Formats.HR, 'address': 0, 'count': 1, 
                'period': 0.5}
    
    
    
    # asyncio.run(test_connection(module['ip'], module['port'], module['addr_pool'], module['address'], module['count'], module['unit'], ))
    # asyncio.run(test_source(module))
    # asyncio.run(test_source_pool(source_list))
    asyncio.run(test_exchange_server(source_list, modbus_server_1))
    MBServerAdrMap=[
            {'unit':0x1, 
                'map':{
                    'di':[{'addr':1,'length':2},
                          {'addr':3,'length':2}],
                    'hr':[  {'addr':0,'length':2},
                            {'addr':6,'length':20},]
                }
            }]
    # asyncio.run(test_ModBusServer(MBServerAdrMap, [module], '127.0.0.1', 5021))
    
    