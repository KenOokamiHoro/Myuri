import asyncio
import requests
import re

def searx_search(keyword,amount):
    '''The actual founction which make searx search.'''
    query = requests.get("https://searx.yoitsu.moe/?q=%22{}%22&format=json".format(keyword)).json()
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
    keyword = arg['keyword']
    try:
        result = searx_search(keyword,amount)
    except json.decoder.JSONDecodeError:
        send("╮(￣▽￣)╭ sad story... No results found, or used incorrect search syntax.")
    else:
        for item in result:
            send("[From {}] {} | [ {} ] {}".format(",".join(item['engines']),
                                                   item['title'],
                                                   item['url'],
                                                   (item['content'][:100]+"..." if len(item['content']) > 101 else item['content'])))


help = [
    ('searx'          , 'searx[:amount] <keyword> -- Get first <amount> results from searx (amount<=3).'),
]

func = [
    (searx            , r"searx(?::(?P<amount>\S+))?\s+(?P<keyword>.+)"),
]
