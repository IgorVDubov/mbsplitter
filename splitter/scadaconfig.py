from .handlers.splitter import splitter
# from handlerslib.bitstoword import bits_to_word


from consts import AI, DI, LIST

'''
Список опрашиваемых модулей
id->str: для идентификации
type->str: тип устройства, реализовано: ModbusTcp
ip->str: ip или testN, тест - эммулятор сигнала с алгоритмом работы задающимся N
port->int: порт модуля
unit->int: номер устройства (в ТСР обычно 1, если ТСР конвертер в 485 - номер в 485-й сети)
address->int: с какого адреса начинаес читать данные
count->int: кол-во адресов для чтения
function->int: модбас функция: реализованы: 2-read_discrete_inputs, 3-read_holding_registers, 4-read_input_registers  
format->str: AI - массив бит, DI - массив чисел длинной count*8 if func=2 or count*16 if func=3|4
period->float: период опроса в сек
handler->callable: функция предобработки данных из channel_handlers 
''' 
module_list=[ 
            # {'id':'2001AI','type':'ModbusTcp','ip':'192.168.1.200','port':503,'unit':0x0, 'address':1, 'regCount':2, 'function':3, 'format':LIST, 'period':2},
            # {'id':'2001DI','type':'ModbusTcp','ip':'192.168.1.200','port':503,'unit':0x0, 'address':2, 'regCount':2, 'function':3, 'format':LIST, 'period':2},
            {'id':'2021AI','type':'ModbusTcp','ip':'172.19.10.7','port':502,'unit':0x1, 'address':0, 'regCount':1, 'function':4, 'format':LIST, 'period':0.5},
            {'id':'2020DI','type':'ModbusTcp','ip':'172.19.10.7','port':502,'unit':0x1, 'address':0, 'regCount':8, 'function':2, 'format':LIST, 'period':0.5},
            # {'id':'2001AI','type':'ModbusTcp','ip':'172.19.10.9','port':502,'unit':0x1, 'address':0, 'regCount':1, 'function':4, 'format':LIST, 'period':0.5},
            # {'id':'2001DI','type':'ModbusTcp','ip':'172.19.10.9','port':502,'unit':0x1, 'address':0, 'regCount':8, 'function':2, 'format':LIST, 'period':0.5},
            # {'id':'2001counter','type':'ModbusTcp','ip':'172.19.10.9','port':502,'unit':0x1, 'address':1, 'regCount':1, 'function':3, 'format':LIST, 'period':0.5},
            ]    
  

'''
словарь конфигурации каналов:
{'id':4209,'moduleId':'test3','type':'AI','sourceIndexList':[0], 
            'handler':channel_handlers.middle10,
            'args':{'name':val,...}}
id->int: id объекта контроля
moduleId->str: модуль с входами датчиков от  объекта контроля
type->str: di биты состояния, ai- аналоговые данные - одно значение, нет группового чтения
type-> DI биты состояния, AI- аналоговые данные - одно значение, нет группового чтения, LIST - массив регистров
sourceIndexLISTist->list: позиции (индексы с 0) данных массива результата чтения модуля moduleId
handler->str: имя функции обработчика результата (в модуле handler_funcs)
args: запись аргументов: 
    'args':{
        'argName1':value[число] в args создается аргумент с именем argName1 и значением value 
        'argName1':'id' в args создается аргумент с именем argName1 и привязкой к объекту канала id 
        'argName1':'id.arg' в args создается аргумент с именем argName1 и привязкой к аргументу arg объекта канала id 
        'argName1':'id.arg.v1' в args создается аргумент с именем argName1 и привязкой к аргументу arg.v1 объекта канала id 
        'argName1':'self.v1' в args создается аргумент с именем argName1 и привязкой к аргументу v1 этого канала 
}
'''   
channels_config={
    'channels':[
        {'id':1001},    #2001AI
        {'id':1002},    #2001DI
        # {'id':1003},    #2001counter
    ],
    'nodes':[  
                {'id':4001,'moduleId':'2001AI','type':LIST,'sourceIndexList':[0],'handler':splitter,
                            'args':{'result_in':'4001.resultIn',
                                    'result_out':'4001.result',
                                    'out':'1001.result',
                                    }},
                {'id':4002,'moduleId':'2001DI','type':LIST,'sourceIndexList':[0],'handler':splitter,
                            'args':{'result_in':'self.resultIn',
                                    'result_out':'self.result',
                                    'out':'1002.result',
                                    }},
                # {'id':4003,'moduleId':'2001counter','type':LIST,'sourceIndexList':[0],'handler':splitter,
                #             'args':{'result_in':'self.resultIn',
                #                     'result_out':'self.result',
                #                     'out':'1003.result',
                #                     }},
    ],
    'programms':[
    ],
    'dbquie':[
        ]
}


#
# разметка адресов Модбас сервера для внешнего доступа
# unit->int: номер unit-а по умолчанию 1
# map ->dict: общее:
#                 id->int: id объекта контроля
#                 addr->int: адрес (смещение) первого регистра

#             di - discrete_inputs чтение функцией 2
#                 len->int: кол-во регистров (bytes)
#             hr - holding_registers чтение функцией 3
#             ir - input_registers чтение функцией 4
#                 type:      FLOAT - 2xWord CD-AB(4Byte);
#                            INT - 1xWord (2Byte)
#                            LIST - list of Words, 'length' - number of words in list
                                
                                
# mb_server1_addr_map=[
#     {'unit':0x1, 'map':{
#             'hr':[{'id':4001, 'attr':'result', 'addr':1, 'type':LIST, 'length':2},
#                 {'id':4002, 'attr':'result', 'addr':3, 'type':LIST, 'length':2}],
#             }}]
# mb_server2_addr_map=[
#     {'unit':0x1, 'map':{
#             'hr':[  {'id':1001, 'attr':'result', 'addr':1, 'type':LIST, 'length':2},
#                     {'id':1002, 'attr':'result', 'addr':3, 'type':LIST, 'length':2}],
#             }}]
mb_server1_addr_map=[
    {'unit':0x1, 'map':{
            'di':[{'id':4002, 'attr':'result', 'addr':0, 'type':LIST, 'length':8},],
            'ir':[{'id':4001, 'attr':'result', 'addr':0, 'type':LIST, 'length':2},],
            # 'hr':[{'id':4003, 'attr':'result', 'addr':1, 'type':LIST, 'length':1}],
            }}]
mb_server2_addr_map=[
    {'unit':0x1, 'map':{
            'di':[{'id':1002, 'attr':'result', 'addr':0, 'type':LIST, 'length':8},],
            'ir':[{'id':1001, 'attr':'result', 'addr':0, 'type':LIST, 'length':2},],
            # 'hr':[{'id':1003, 'attr':'result', 'addr':1, 'type':LIST, 'length':1},],
            }}]


