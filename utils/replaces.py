import re

teleboto = re.compile(r'(\\x0\d*[abcdef]?)')

def erase(mode,text):
    return mode.sub("",text)