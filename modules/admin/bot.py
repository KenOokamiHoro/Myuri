'''some tools to control bot itself.'''

import asyncio

@asyncio.coroutine
def reload(bot, nick, message, target, send):
    '''reload!'''
    if nick != bot.admin or message != "'!reload":
        return

    print('reload')
    try:
        bot.reload()
        send('reloaded')
    except Exception:
        send('error')
        raise

func = [
    (reload,r"reload"),
]
