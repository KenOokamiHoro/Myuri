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


help = [
    ('wiki'          , 'wiki[:lang] <keyword> -- Get <keyword> in <lang> wikipedia.'),
]

func = [
    (wiki            , r"wiki(?::(?P<lang>\S+))?\s+(?P<keyword>.+)"),
]
