from time import time

from loguru import logger

from channels import channels
from myexceptions import ChannelException, ConfigException

CHANNELS_EXEC_ORDER=[channels.Node,channels.Channel,channels.Programm, channels.DBQuie]

class ChannelsBase():
    def __init__(self):
        self.channels=[]
        self.channelsExecTime=None
    
    def add(self,channel:channels.Channel):
        try:
            found=next(filter(lambda _channel: _channel.id == channel.id, self.channels))
        except StopIteration:
            found=None
        if not found:
            if len(self.channels):
                try:
                    for ch in self.channels:
                        if CHANNELS_EXEC_ORDER.index(type(ch))>CHANNELS_EXEC_ORDER.index(type(channel)):
                            # print (f'insert channel {channel.id} ' )
                            self.channels.insert(self.channels.index(ch),channel)
                            return
                except ValueError:
                    logger.warning(f'cant find order on CHANNELS_EXEC_ORDER for channel {channel.id}, move to end')
            self.channels.append(channel)
            # print (f'append channel {channel.id} ' )
        else:
            raise ConfigException(f'duplicate id in channel base adding {channel} ')
    
    def get(self, id:int)->channels.Channel:
        try:
            found=next(filter(lambda _channel: _channel.id == id, self.channels))
        except StopIteration:
            found=None
        return found

    def execute(self, id:int):
        channel=self.get(id)
        try:
            result=channel()
        except ChannelException as e:
            logger.error(e)
        return result
    # def executeAll(self):
    #     for channelType in CHANNELS_EXEC_ORDER:
    #         for channel in [ch for ch in self.channels if isinstance(ch, channelType)]:
    #             print(f'exec {channel.id}')
    #             channel()
    def executeAll(self):
        startTime=time()
        for channel in self.channels:
            print(f'exec {channel.id}')
            channel()
        self.channelsExecTime=time()-startTime

    def nodesToDict(self):
        result=dict()
        result.setdefault(channels.Node.__name__.lower(),[])
        for channel in self.channels:
            if isinstance(channel, channels.Node):
                result[channels.Node.__name__.lower()].append(channel.toDict())
        return result
    
    def nodesToDictFull(self):
        result=dict()
        result.setdefault(channels.Node.__name__.lower(),[])
        for channel in self.channels:
            if isinstance(channel, channels.Node):
                result[channels.Node.__name__.lower()].append(channel.toDictFull())
        return result
    
    def toDict(self):
        result=dict()
        for chType in CHANNELS_EXEC_ORDER:          #!!! если нет нового класса канала в массиве - не будет включен!!!!!!!!
            result.setdefault(chType.__name__.lower(),[])
        for channel in self.channels:
            result[channel.__class__.__name__.lower()].append(channel.toDict())
        return result
    
    def toDictFull(self):
        result=dict()
        for chType in CHANNELS_EXEC_ORDER:          #!!! если нет нового класса канала в массиве - не будет включен!!!!!!!!
            result.setdefault(chType.__name__.lower(),[])
        for channel in self.channels:
            result[channel.__class__.__name__.lower()].append(channel.toDictFull())
        return result

    def __str__(self) -> str:
        return ''.join(channel.__str__()+'\n' for channel in self.channels )

def channel_base_init(channelsConfig, dbQuie):
    # сначала у всех каналов создаем аттрибуты, потом привязываем связанные
    bindings=[]
    dbQuieChannel=False
    chBase=ChannelsBase()
    for channelType in channelsConfig:
        chType=eval(channels.CHANNELS_CLASSES.get(channelType))
        if chType==channels.Channel:
            cls=channels.Channel
        elif chType==channels.Node:
            cls=channels.Node
        elif chType==channels.Programm:
            cls=channels.Programm
        elif chType==channels.DBQuie:
            cls=channels.DBQuie
            dbQuieChannel=True
        elif chType==channels.DBconnector:
            cls=channels.DBQuie
        else:
            raise ConfigException(f'no type in classes for {chType} {channelType}')
        for channelConfig in channelsConfig.get(channelType):
            if dbQuieChannel:
                channelConfig.update({'dbQuie':dbQuie})
            if channelConfig.get('args'):
                args=channelConfig.pop('args')
                channel=cls(**channelConfig)
                for name, arg in args.items():
                    bindId, param= channels.parse_attr_params(arg)
                    if bindId != None:
                        channel.addArg(name)
                        bindings.append((channel, name, bindId, param))
                    else:
                        channel.addArg(name, param)
            else:
                channel=cls(**channelConfig)
            chBase.add(channel)
        dbQuieChannel=False
    for (channel2Bind, name, bindId, param) in bindings:
        if bindId=='self':
            channel2Bind.bindArg(name, channel2Bind, param)
        elif bindId and param:
            if bindChannel:=chBase.get(bindId):
                channel2Bind.bindArg(name, bindChannel, param)
            else:
                raise ConfigException(f'Cant find channel {bindId} when binding to {channel2Bind.id}')
        elif bindId and param==None:
            if bindChannel:=chBase.get(bindId):
                channel2Bind.bindChannel2Arg(name, bindChannel)
            else:
                raise ConfigException(f'Cant find channel {bindId} when binding in {channel2Bind.id}')
    bindings=[]
    return chBase

def bindChannelAttr(channelBase, id:int,attrNmae:str)->channels.Vars:
    '''
    id- channel id
    attrname:str - channel attribute mane 
    '''
    if channel:=channelBase.get(id):
        bindVar=channels.Vars()
        bindVar.addBindVar('value',channel,attrNmae)
        return bindVar
    else:
        raise ConfigException(f'Cant find channel {id} in channelBase')

if __name__ == '__main__':
    nodes=[  
            #{'id':4207,'moduleId':'ModuleA','type':'DI','sourceIndexList':[0,1],'handler':'func_1'},
            # {'id':4208,'moduleId':'ModuleB','type':'AI','sourceIndexList':[0]},
            {'id':4208,'moduleId':'test2','type':'DI','sourceIndexList':[0,1]},
            {'id':4209,'moduleId':'test3','type':'AI','sourceIndexList':[0]}
            ]
    import handlers
    prgs=[{'id':10001, 'handler':handlers.progvek, 'args':{'ch1':{'id':4208,'arg':'result'},'result':{'id':4209,'arg':'resultIn'}}, 'stored':{'a':0}}]
    cb=channel_base_init(nodes, prgs) 
    print(cb)
    cb.get(4208).result=44
    cb.execute(10001)
    print(cb)
    cb.get(4208).result=50
    cb.execute(10001)
    print(cb)
    cb.executeAll()
    print(cb.channelsExecTime)
 