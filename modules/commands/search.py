import asyncio
import requests
import re

def searx_search(keyword,lang="all",amount=1):
    '''The actual founction which make searx search.'''
    query = requests.get('https://searx.yoitsu.moe/?q={}&format=json&language={}'.format(keyword,lang)).json()
    try:
        results = query['results'][:amount]
    except IndexError:
        results = query['results']
    return results
 
    

@asyncio.coroutine
def searx(arg,send):
    try:
        if int(arg['amount']) >3:
            amount = 3
        else:
            amount = int(arg['amount'])
    except TypeError:
        amount = 1
    if arg['lang']:
        language = arg['lang']
    else:
        language = 'all'
    keyword = arg['keyword']
    try:
        result = searx_search(keyword,language,amount)
    except json.decoder.JSONDecodeError:
        send("╮(￣▽￣)╭ sad story... No results found, or used incorrect search syntax.")
    else:
        for item in result:
            send("[From {}] {} | [ {} ] {}".format(",".join(item['engines']),
                                                   item['title'],
                                                   item['url'],
                                                   (item['content'][:100]+"..." if len(item['content']) > 101 else item['content'])))


help = [
    ('searx'          , 'searx[:amount][:lang] <keyword> -- Get first <amount> results from searx (amount<=3) in <lang> language.'),
]

func = [
    (searx            , r"searx(?::(?P<amount>\d+))?(?::(?P<lang>\S+))?\s+(?P<keyword>.+)"),
]
