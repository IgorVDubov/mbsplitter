import os.path

from consts import Consts


# PROJECT={'name':'Empty','path':'empty','comment':''}
PROJECT={'name':'Idle demo machines','path':'idledemo','comment':''}
PATH_TO_PROJECT=os.path.join(os.path.dirname(__file__),'projects',
                            PROJECT.get('path','/'))
# project_path= os.path.join(PROJECT.get('path','/'),  'templates'),

# HTTPServerParams={'host':'127.0.0.1','port':8870,'wsserver':'ws://127.0.0.1:8870/ws'}
HTTPServerParams={'host':'192.168.1.200','port':8870,'wsserver':'ws://192.168.1.200:8870/ws'}
CHECK_AUTORIZATION=True

users=[
    {'id': 1, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div', 'pass': '123'},
    {'id': 2, 'first_name': 'Igor', 'middle_name': '', 'second_name': 'Dubov', 'login': 'div1', 'pass': '123'},
    {'id': 3, 'first_name': '5001', 'middle_name': '', 'second_name': '', 'login': 'm_5001', 'pass': 'm777'},
    {'id': 4, 'first_name': '2020', 'middle_name': '', 'second_name': '', 'login': 'm_2020', 'pass': 'm777'},
    ]


DB_PERIOD=3    #период опроса очереди сообщений для БД DBQuie


CHANNELBASE_CALC_PERIOD=2 #период пересчета каналов в секундах (float) 

MBServer1_params={'host':'127.0.0.1','port':510}
MBServer2_params={'host':'127.0.0.1','port':511}
'''
параметры Модбас сервера для внешнего доступа
host, port->str: An optional (interface, port) to bind to.
'''
MBServerParams_E={'host':'127.0.0.1','port':5022}
'''
параметры эмулятора Модбас сервера 
host:str, port:itn  An optional (interface, port) to bind to.
'''
DB_TYPE=Consts.MYSQL        #тип используемой СУБД (доступные в dbclassfactory)
MySQLServerParams={
    'host': '127.0.0.1',
    'database': 'utrack_demo',
    'user': 'utrack',                       #TODO в переменные окружения!!!!!
    'password' : 'Adm_db78'
}
'''
параметры MySQLServer
'''
DB_PARAMS=MySQLServerParams     #параметры для инициализации текущей СУБД
