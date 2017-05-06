import asyncio
import requests
import re
import subprocess

class Notinofficial(Exception):
    '''This package is not in official repoisitories'''
    pass

class NoResultinofficial(Exception):
    '''This package is not in official repoisitories'''
    pass

class NotinAUR(Exception):
    '''This package is not in AUR'''
    pass

class NoResultinAUR(Exception):
    '''This package is not in AUR'''
    pass

def official_package(pkgname):
    '''Find a Arch Linux Package exactly through web interface.'''
    url="https://www.archlinux.org/packages/search/json/?name={}&arch=any&arch=x86_64"
    try:
        package = requests.get(url.format(pkgname)).json()['results'][0]
    except IndexError:
        raise Notinofficial()
    else:
        return package

def search_official_package(keyword):
    '''Search official packages.'''
    url="https://www.archlinux.org/packages/search/json/?q={}&arch=any&arch=x86_64"
    try:
        query = requests.get(url.format(keyword)).json()['results']
        pkgnames = query[:5]
    except IndexError:
        pkgnames = query
    finally:
        if not pkgnames:
            raise NoResultinofficial()
        else:        
            return [pkg['pkgname'] for pkg in pkgnames]

def search_aur_package(keyword):
    '''Search AUR packages.'''
    url="https://aur.archlinux.org/rpc/?v=5&type=search&by=name-desc&arg={}"
    try:
        query = requests.get(url.format(keyword)).json()['results']
        pkgnames = query[:5]
    except IndexError:
        pkgnames = query
    finally:
        if not pkgnames:
            raise NoResultinAUR()
        else:        
            return [pkg['Name'] for pkg in pkgnames]

def official_package_text(package):
    '''Make message text though json.'''
    pkgname = package['pkgname']
    pkgdesc = package['pkgdesc']
    pkgarch = package['arch']
    pkgver = package['pkgver']+'-'+package['pkgrel']
    flag_date = package['flag_date']
    repo = package['repo']
    pkgurl = "https://www.archlinux.org/packages/{}/{}/{}/".format(repo,pkgarch,pkgname)
    template = "[{}/{}] ({}),version {} ,{}. More information on website: {}"
    text = template.format( repo,
                            pkgname,
                            pkgdesc,
                            pkgver,
                            (",flagged out of date on {}".format(flag_date) if flag_date else ""),
                            pkgurl)
    return text

def aurweb(package):
    '''Find a AUR Package exactly through AURWeb.'''
    url = "https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={}"
    try:
        package = requests.get(url.format(package)).json()['results'][0]
    except IndexError:
        raise NotinAUR()
    else:
        return package

def aurweb_text(package):
    '''Make message text though json.'''
    pkgname = package['Name']
    pkgdesc = package['Description']
    pkgver = package['Version']
    maintainer = package['Maintainer']
    pkgurl = "https://aur.archlinux.org/packages/{}/".format(pkgname)
    template = "[AUR] {} ({}),version {} ,maintained by {}. More information on website: {}"
    text = template.format(pkgname,
                           pkgdesc,
                           pkgver,
                           maintainer,
                           pkgurl)
    return text

@asyncio.coroutine
def pacman(arg,send):
    '''Find a Arch Linux Package exactly through web interface.'''
    try:
        text = official_package_text(official_package(arg['package']))
    except Notinofficial:
        send("Package '{}' not found, may it isn't in official repositories or it is a group?".format(arg['package']))
    else:
        send(text)

@asyncio.coroutine
def aur(arg,send):
    '''Find a AUR Package exactly through AURWeb.'''
    try:
        text = aurweb_text(aurweb(arg['package']))
    except NotinAUR:
        send("Error: Package '{}' not found in AUR.".format(arg['package']))
    else:
        send(text)

@asyncio.coroutine
def yaourt(arg,send):
    try:
        send(official_package_text(official_package(arg['package'])))
    except Notinofficial:
        try:
            send(aurweb_text(aurweb(arg['package'])))
        except NotinAUR:
            if arg['option'] == 'exact' :
                send("	╮(￣▽￣)╭  {} is not in official repoistories or AUR.".format(arg['package']))
                return
            try:
                send("Some package in official repositories match your search: {}".format(search_official_package(arg['package'])))
                send("Use 'pacman <package> to get more information.")
            except NoResultinofficial:
                try:
                    send("Some package in AUR match your search: {}".format(search_aur_package(arg['package'])))
                    send("Use 'aur <package> to get more information.")
                except NoResultinAUR:
                    send("	╮(￣▽￣)╭  No result....")
@asyncio.coroutine
def pkgfile(arg,send):
    if not arg['filename']:
        send("😋 want to be eaten ?")
        return
    proc = subprocess.Popen(["/usr/bin/pkgfile",arg['filename']], stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
    text = proc.stdout.read().strip().split("\n")
    if not text:
        send("😌 {} not in any offial package......".format(arg['filename']))
    else:
        send("{} 😋 => {}".format(text,arg['filename']))

help = [
    ('pacman'          , 'pacman <package name> -- find a package exactly on official repositories'),
    ('aur'             , 'aur <package name> -- find a package exactly on AUR'), 
    ('yaourt'          , 'yaourt[:option] <package> -- search a package in official repoistories or aur. use exact option to find a package.'),
    ('pkgfile'         , 'pkgfile <filename> -- which package have this file?')
#    ('archwiki'        , 'archwiki[:option] <title> -- search ArchWiki titles, use exact option to find a article.'),    
]

func = [
    (pacman            , r"pacman (?P<package>.+)"),
    (aur               , r"aur (?P<package>.+)"),
    (yaourt            , r"yaourt(?::(?P<option>\S+))?\s+(?P<package>.+)"),
    (pkgfile           , r"pkgfile (?P<filename>.+)"),
#    (archwiki          , r"archwiki(?::(?P<option>\S+))?\s+(?P<title>.+)"),   
]
