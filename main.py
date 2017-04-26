'''IRC bot operations.'''
import asyncio
import logging
import irc.client as client
from config import database
import utils.db as db
import random

logging.basicConfig(level=logging.DEBUG)

loop = asyncio.get_event_loop()

dbc=db.dbc(uri=database)

bot = client.Client(loop, 'config',dbc)



@bot.on('CLIENT_CONNECT')
def connect(**kwargs):
    bot.send('NICK', nick=bot.nick)
    bot.send('PASS', password=bot.password)
    bot.send('USER', user=bot.login, realname='Bot using bottom.py')
    bot.send('JOIN', channel=bot.channel)


@bot.on('PING')
def keepalive(message, **kwargs):
    bot.send('PONG', message=message)
    
@bot.on('PRIVMSG')
def privmsg(nick, target, message, **kwargs):
    db.log_message(dbc,target,nick,message)
    if nick == bot.nick:
        return
    (nick, message) = bot.deprefix(nick, message)
    if target == bot.nick:
        sender = lambda m, **kw: bot.sender(nick, m, **kw)
    else:
        sender = lambda m, **kw: bot.sender(target, m, to=nick, **kw)
    
    coros = [f(bot, nick, message, target, sender) for f in bot.modules.privmsg]

    yield from asyncio.wait(coros)


bot.loop.create_task(bot.connect())
bot.loop.run_forever()
