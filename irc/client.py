import asyncio
import importlib
import bottom
import utils.db
import random
from .common import dePrefix, Normalize, splitmessage

class RefuseException(Exception):
    pass

class Client(bottom.Client):

    def __init__(self, loop, config,dbc):
        self.config = importlib.import_module(config)
        super().__init__(self.config.host, self.config.port, **self.config.option)

        self.admin = self.config.admin
        self.nick = self.config.nick
        self.login = self.config.login
        self.password = self.config.password
        self.channel = self.config.channel
        self.key = self.config.key
        self.refuse_value = self.config.refuse_value
        self.no_refuses = self.config.no_refuse_nicks
        self.refuses = self.config.always_refuse_nicks

        # (512 - 2) / 3 = 170
        # 430 bytes should be safe
        # not really, for #archlinux-cn-offtopic
        self.msglimit = 420

        self.deprefix = dePrefix()
        self.normalize = Normalize()
        self.modules = importlib.import_module('modules')
        self.dbc = dbc

        self.refuse_templates=["OAO, 好烦啊, 咱才不要给汝找了呢! 哼!",
                               "汝刚刚说了啥？"]

    def reload(self):
        self.modules = importlib.reload(self.modules)
        self.config = importlib.reload(self.config)
        self.key = self.config.key

    def sendm(self, target, message, *, command='PRIVMSG', to='', raw=False, mlimit=0, color=None, **kw):
        prefix = (to + ': ') if to else ''
        message = ('' if raw else prefix) + self.normalize(message, **kw)
        print(message)
        for (i, m) in enumerate(splitmessage(message, self.msglimit)):
            if mlimit > 0 and i >= mlimit:
                self.send(command, target=target, message=prefix + '太多了啦...')
                break
            self.send(command, target=target, message=m)

    def sendl(self, target, line, n, *, llimit=0, **kw):
        sent = False
        for (i, m) in enumerate(line):
            if llimit > 0 and i >= llimit:
                #d = {k: kw[k] for k in ['command', 'to'] if k in kw}
                #self.sendm(target, '太长了啦...', **d)
                command = kw.get('command', 'PRIVMSG')
                to = kw.get('to', '')
                prefix = (to + ': ') if to else ''
                self.send(command, target=target, message=prefix + '太长了啦...')
                break
            self.sendm(target, m, **kw)
            sent = True
            if n > 0 and i >= (n - 1):
                break
        if not sent:
            raise Exception()

    def sender(self, target, content, *, n=-1, llimit=-1, **kw):
        if n < 0:
            self.sendm(target, content, **kw)
        else:
            if llimit < 0:
                self.sendl(target, content, n, **kw)
            else:
                self.sendl(target, content, n, llimit=llimit, **kw)
        utils.db.log_message(self.dbc,target,self.nick,str(content))

    def refuse(self,target,refuse_text):
        utils.db.log_message(self.dbc,target,self.nick,refuse_text.encode('utf-8'))
    
    def is_refuse(self,nick,target):
        if nick in self.refuses:
            raise RefuseException()
        if nick in self.no_refuses:
            return
        seed = random.random()
        if seed < self.refuse_value:
            raise RefuseException()
