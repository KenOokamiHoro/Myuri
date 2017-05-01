import asyncio
import requests
import re

class NotinOffical(Exception):
    '''This package is not in offical repoisitories'''
    pass

class NoResultinOffical(Exception):
    '''This package is not in offical repoisitories'''
    pass

class NotinAUR(Exception):
    '''This package is not in AUR'''
    pass

class NoResultinAUR(Exception):
    '''This package is not in AUR'''
    pass

def offical_package(pkgname):
    '''Find a Arch Linux Package exactly through web interface.'''
    url="https://www.archlinux.org/packages/search/json/?name={}&arch=any&arch=x86_64"
    try:
        package = requests.get(url.format(pkgname)).json()['results'][0]
    except IndexError:
        raise NotinOffical()
    else:
        return package

def search_offical_package(keyword):
    '''Search offical packages.'''
    url="https://www.archlinux.org/packages/search/json/?q={}&arch=any&arch=x86_64"
    try:
        query = requests.get(url.format(keyword)).json()['results']
        pkgnames = query[:5]
    except IndexError:
        pkgnames = query
    finally:
        if not pkgnames:
            raise NoResultinOffical()
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

def offical_package_text(package):
    '''Make message text though json.'''
    pkgname = package['pkgname']
    pkgdesc = package['pkgdesc']
    pkgarch = package['arch']
    pkgver = package['pkgver']+'-'+package['pkgrel']
    flag_date = package['flag_date']
    repo = package['repo']
    pkgurl = "https://www.archlinux.org/packages/{}/{}/{}/".format(repo,pkgarch,pkgname)
    template = "[Offical repository] {} ({}),version {} ,in [{}]{}. More information on website: {}"
    text = template.format(pkgname,
                            pkgdesc,
                            pkgver,
                            repo,
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
        text = offical_package_text(offical_package(arg['package']))
    except NotinOffical:
        send("Package '{}' not found, may it isn't in offical repositories or it is a group?".format(arg['package']))
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
        send(offical_package_text(offical_package(arg['package'])))
    except NotinOffical:
        try:
            send(aurweb_text(aurweb(arg['package'])))
        except NotinAUR:
            if arg['option'] == 'exact' :
                send("	╮(￣▽￣)╭  {} is not in offical repoistories or AUR.".format(arg['package']))
                return
            try:
                send("Some package in offical repositories match your search: {}".format(search_offical_package(arg['package'])))
                send("Use 'pacman <package> to get more information.")
            except NoResultinOffical:
                try:
                    send("Some package in AUR match your search: {}".format(search_aur_package(arg['package'])))
                    send("Use 'aur <package> to get more information.")
                except NoResultinAUR:
                    send("	╮(￣▽￣)╭  No result....")


help = [
    ('pacman'          , 'pacman <package name> -- find a package exactly on offical repositories'),
    ('aur'             , 'aur <package name> -- find a package exactly on AUR'), 
    ('yaourt'          , 'yaourt[:option] <package> -- search a package in official repoistories or aur. use exact option to find a package.'),
#    ('archwiki'        , 'archwiki[:option] <title> -- search ArchWiki titles, use exact option to find a article.'),    
]

func = [
    (pacman            , r"pacman (?P<package>.+)"),
    (aur               , r"aur (?P<package>.+)"),
    (yaourt            , r"yaourt(?::(?P<option>\S+))?\s+(?P<package>.+)"),
#    (archwiki          , r"archwiki(?::(?P<option>\S+))?\s+(?P<title>.+)"),   
]
