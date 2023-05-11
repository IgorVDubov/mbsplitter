from gather.consts import Formats, SourceTypes
'''
Список опрашиваемых модулей
id->str: для идентификации
type->str: тип устройства, реализовано: SourceTypes.MODBUS_TCP
ip->str: ip источника
port->int: порт источника
unit->int: номер устройства (в ТСР обычно 1, если ТСР конвертер в 485 - номер в 485-й сети)
addr_pool: раздел таблицы адресов из consts.Formats CO | DI | HR | IR
address->int: начальный адрес чтения данных
count->int: кол-во последовательных адресов для чтения
period->float: период опроса в сек
'''
module_list = [
    {'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.7', 'port': 502, 'unit': 0x1,
        'addr_pool': Formats.IR, 'address': 0, 'count': 1, 'period': 0.5},
    {'type': SourceTypes.MODBUS_TCP, 'ip': '172.19.10.7', 'port': 502, 'unit': 0x1,
        'addr_pool': Formats.DI, 'address': 0, 'count': 8, 'period': 0.5},
]


modbus_server_1 = {'host': '127.0.0.1', 'port': 510}
modbus_server_2 = {'host': '127.0.0.1', 'port': 511}
