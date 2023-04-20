import os.path


def get_config(params, PATH_TO_PROJECT):
    settings = {
        #'static_path': os.path.join(os.path.dirname(__file__), "static"),
        'template_path': os.path.join(PATH_TO_PROJECT, 'web' ,'webdata'),
        # 'template_path': os.path.join(params.get('path'), 'webserver','webdata','templates'),
        'debug': True,
        #'debug': False,
        'cookie_secret':"61ofdgETxcvGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
        'wsParams':params.get('wsserver','ws://localhost:8888/ws')
        }
    return settings