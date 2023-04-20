'''
модуль обмена данными по запросам от внешних клиентов
реализация : ModBus

'''
from abc import ABC, abstractmethod
from copy import deepcopy

import channels.channelbase as channelbase
import modbus_server


class ExchangeServer(ABC):
    
    @abstractmethod
    def start():...
    @abstractmethod
    def stop():...
    @abstractmethod
    def setValue():...
    @abstractmethod
    def getValue():...

    



class ModbusExchangeServer(ExchangeServer):
    def __init__(self,addrMapP:list,serverHost, serverPort, loop):
        
            self.server=modbus_server.MBServer(addrMapP,{'host':serverHost, 'port':serverPort},loop=loop)
    
    def start(self):
        self._mbStart()
    def stop(self):
        self._mbStop()
    def setValue(self,id,value):
        self._mbSetIdValue(id,value)
    def getValue(self, id): 
        return self._mbGetIdValue(id)

    def _mbStart(self):
        # self.server.startInThread()
        self.server.start()
    
    def _mbStop(self):
        self.server.stop()
    
    def _mbSetIdValue(self,id,value):
        self.server.setValue(id,value)
    def _mbGetIdValue(self,id):
        return self.server.getValue(id)

def MBServerAdrMapInit(channelBase:channelbase.ChannelsBase, addrMaping:dict )->tuple():
    '''
    привязка атрибутов каналов из addrMaping к атрибутам каналов из channelBase
    return
    channelBase у которой убраны поля привязки для совместимости с  MBServer
    bindings {channelID:binding} - словарь привязок для ускорения обработки
    '''
    newAddrMap=deepcopy(addrMaping)
    bindings=dict()
    for unit in  newAddrMap:
        for regType,data in unit.get('map').items():
            for reg in data:
                if attr:=reg.pop('attr'):
                    bindings.update({reg['id']: channelbase.bindChannelAttr(channelBase,reg['id'],attr)})
                else:
                    raise ValueError(f'no value to bind at {reg}')
    return newAddrMap, bindings

if __name__ == '__main__':
    pass
