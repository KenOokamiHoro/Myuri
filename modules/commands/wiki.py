import asyncio
import requests
import re

class NoResultException(Exception):
    pass

def search_wikipedia(keyword,lang="en"):
    '''search wikipedia'''
    baseurl = 'https://{}.wikipedia.org/w/api.php?action=opensearch&search={}&redirects=resolve&format=json&utf8=true'
    query = requests.get(baseurl.format(lang,keyword)).json()
    if not query[1]:
        raise NoResultException()
    return (query[2][0],query[3][0])
    

def search_mediawiki(api,keyword,mode="opensearch",textextract=False):
    baseurl = '{}?action={}&search={}&redirects=resolve&format=json&utf8=true'
    query = requests.get(baseurl.format(api,mode,keyword)).json()
    if not query[1]:
        raise NoResultException()
    if textextract:
        return (query[2][0],query[3][0])
    else:
        return (query[3][0],)
    
@asyncio.coroutine
def wiki(arg,send):
    lang = arg.get("lang","en")
    keyword = arg['keyword']
    try:
        result = search_wikipedia(keyword,lang)
    except NoResultException:
        send("╮(￣▽￣)╭ sad story... No results found.")
    except requests.exceptions.SSLError:
        send("╮(￣▽￣)╭ {} is not a vaild language.".format(lang))
    else:
        send("{} -> {} ".format(*result))

@asyncio.coroutine
def devi(arg,send):
    keyword = arg['keyword']
    try:
        result = search_mediawiki("https://wikidevi.com/w/api.php",keyword)
    except NoResultException:
        send("╮(￣▽￣)╭ sad story... No results found.")
    else:
        send("{}".format(*result))

help = [
    ('wiki'          , 'wiki[:lang] <keyword> -- Get <keyword> in <lang> wikipedia.'),
    ('devi'          , 'devi <keyword> -- Get <keyword> in wikidevi.org'),
    
]

func = [
    (wiki            , r"wiki(?::(?P<lang>\S+))?\s+(?P<keyword>.+)"),
    (devi            , r"devi\s+(?P<keyword>.+)"),
    
]
