from loguru import logger
import globals
import os.path
PATH_TO_PROJECT=os.path.join(os.path.dirname(__file__),'projects',
                            globals.PROJECT['path'])
from globals import CHECK_AUTORIZATION
from globals import PROJECT

import tornado.web
import tornado.websocket

RequestHandlerClass=tornado.web.RequestHandler
StaticFileHandler=tornado.web.StaticFileHandler
RequestHandler=tornado.web.RequestHandler
WebSocketHandler=tornado.websocket.WebSocketHandler



class BaseHandler(RequestHandlerClass):
    user=None
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def getUser(self):
        '''
        return dict with user data if user belongs to project with projectId or None
        '''
        if not self.current_user:
            return None
        try:
            userId = int(tornado.escape.xhtml_escape(self.current_user))
            # user=[user for user in self.application.data.users if user['id']==userId][0]
            if  user:=next(filter(lambda user: user['id'] == userId, self.application.data.users)):  
                logger.debug('user '+user['login']+' ok')
                return user
            else:
               return None
        except TypeError or ValueError:
            return None
    
    def check_user(check_authorization=True): 
        def decorator(handler_func):
            def wrapper(self, *args, **kwargs):
                user={}
                if not check_authorization or (user:=self.getUser()):
                    self.user=user
                    handler_func(self, *args, **kwargs)
                else:
                    self.redirect("/login")
            return wrapper
        return decorator    

class MainHtmlHandler(BaseHandler):
    
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def get(self):
        print (f'in MainHtmlHandler, project {PROJECT["name"]}, user {self.user} ')
        self.render('index.html', user=self.user.get('login'),wsserv=self.application.settings['wsParams'])
    
    
class RequestHtmlHandler(BaseHandler):
    @BaseHandler.check_user(CHECK_AUTORIZATION)
    def post(self):
        self.set_header("Content-Type", "application/json")
        request=json.loads(self.request.body)
        if request.get('type')=='allStateQuerry':
            logger.log('MESSAGE',f'client {user["login"]} do allStateQuerry from ip:{self.request.remote_ip}.')
            self.write(json.dumps(self.application.data.channelBase.toDict(), default=str))
    
    
    def get(self):
        pass
        self.set_header("Content-Type", "application/x-www-form-urlencoded")
        requestHeader=self.request.headers
        print (f'GET request!!!!!!!!!!!!!')
        print (f'requestHeader:{requestHeader}')
        requestBody=self.request.body
        print (f'requestBody:{requestBody}')

class WSHandler(tornado.websocket.WebSocketHandler):
    def initialize(self, clbk):
        self.callback=clbk
    def __init__(self, *args, **kwargs):
        self.id = None
        super(WSHandler, self).__init__(*args, **kwargs)
    
    # def check_origin(self, origin: str) -> bool:
        #print(f'origin:{origin}')
        # сюда можно проверку хостов с которых запросы
        #return self.current_user != None  #ws запросы только если кто-то залогинился перед этим
        # return True
        #return super().check_origin(origin)

    def open(self):
            logger.info(f'Web Socket open, IP:{self.request.remote_ip} Online {len(self.application.wsClients)} clients')
            # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота и не включаем его в список ws рассылки
            #     #if tornado.escape.xhtml_escape(self.get_secure_cookie("user")) in [_ for _ in allUsers(users)]:
            if self not in self.application.wsClients:
                self.application.wsClients.append(self)
            #         user=[user for user in globals.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
            #         logger.info(f'Web Socket open, IP:{self.request.remote_ip},  user:{user.get("login")}, Online {len(globals.wss)} clients')
            #     else:
            #         logger.log ('LOGIN',f'websocket user {tornado.escape.xhtml_escape(self.get_secure_cookie("user"))} not autirized , IP:{self.request.remote_ip}')
            #         self.close()
        
    def on_message(self, message):
        try:
            jsonData = json.loads(message)
        except json.JSONDecodeError:
            logger.error ("json loads Error for message: {0}".format(message))
        else:
            if jsonData['type']=="allStateQuerry":
                logger.debug ("ws_message: allStateQuerry")
                msg = {'type':'mb_data','data': None}
                json_data = json.dumps(msg, default=str)
                self.write_message(json_data)
            elif jsonData['type']=="testMsg":
                pass
            elif jsonData['type']=="msg":
                logger.debug (f"ws_message: {jsonData['data']}")
            else:
                logger.debug('Unsupported ws message: '+message)        
 
    def on_close(self):
        # if self.request.headers['User-Agent'] != 'UTHMBot':  #не логгируем запросы от бота
        #     user=[user for user in globals.users if user['id']==int(tornado.escape.xhtml_escape(self.get_secure_cookie("user")))][0]
        #     logger.info(f' User {user.get("login")} close WebSocket. Online {len(self.application.wsClients)-1} clients')
        if self in self.application.wsClients:
            self.application.wsClients.remove(self)
        # if len(globals.wss)==0:
            # print('No online users, callback stops')
            # self.callback.stop()


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.get_argument("name", "")
        
        for user in self.application.data.users:
            if user['login']==username:
                logger.log('DEBUG',f"Try login {username}, user ok, ip:{self.request.remote_ip}")
                #self.set_secure_cookie("user", username, expires_days=180)
                self.set_secure_cookie("user", str(user.get('id') ), expires_days=180)
                self.redirect("/")
                return
        # no such user
        logger.log('DEBUG',f"Try login {username}, user wrong , ip:{self.request.remote_ip}")
        self.redirect("/login")

class LogoutHandler(BaseHandler):

    def get(self):
        self.clear_cookie("user")
        self.redirect("/login")


handlers=[
        (r"/", MainHtmlHandler),
        (r"/login",LoginHandler),
        (r"/logout",LogoutHandler),
        (r"/request", RequestHtmlHandler),
        # (r'/ws', WSHandler, dict(clbk=None)),
        (r"/static/(.*)", StaticFileHandler, {"path": 'PATH_TO_PROJECT'+'web/webdata'}),
        (r'/js/(.*)', StaticFileHandler, {'path': 'PATH_TO_PROJECT'+'web/webdata/js'}),
        (r'/css/(.*)', StaticFileHandler, {'path': 'PATH_TO_PROJECT'+'web/webdata/css'}),
        (r'/images/(.*)', StaticFileHandler, {'path': 'PATH_TO_PROJECT'+'web/webdata/images'}),
        ]
