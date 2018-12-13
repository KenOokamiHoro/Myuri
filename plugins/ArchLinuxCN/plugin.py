###
# Copyright (c) 2018, KenOokamiHoro
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import re
import requests

import supybot.commands
import supybot.callbacks
import supybot.log
import supybot.plugins

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization('ArchLinuxCN')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    def _(x):
        return x


class ArchLinuxCN(supybot.callbacks.Plugin):
    """Some useful commands in Arch Linux CN Community channels."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(ArchLinuxCN, self)
        self.__parent.__init__(irc)

    @supybot.commands.wrap(['anything'])
    def pacman(self, irc, msg, args, package, recipt=None):
        '''<package>

        Find <package> in Arch Linux offical repositories exactly.
        '''
        try:
            text = official_package_text(official_package(package))
        except not_in_offical:
            irc.reply(
                "Package '{}' not found, may it isn't in official repositories or it is a group?".format(package))
        else:
            for line in text:
                irc.reply(line)

    @supybot.commands.wrap(['anything'])
    def aur(self, irc, msg, args, package):
        '''<package>

        Find a AUR Package exactly through AURWeb exactly.'''
        try:
            text = aurweb_text(aurweb(package))
        except not_in_aur:
            irc.reply("Error: Package '{}' not found in AUR.".format(package))
        else:
            for line in text:
                irc.reply(line)

    @supybot.commands.wrap(['anything'])
    def cnbuild(self, irc, msg, args, package):
        '''<package>

        Get latest build status of [archlinuxcn] packages.'''
        try:
            text = archlinuxcn_package_text(archlinuxcn_package(package))
        except not_in_archlinuxcn:
            irc.reply(
                "Error: Package '{}' not found in [archlinuxcn].".format(package))
        else:
            for line in text:
                irc.reply(line)

    def do_privmsg_notice(self, irc, msg):
        channel, nick, text = msg.args[0], msg.nick, msg.args[-1]
        if not irc.isChannel(channel):
            return
        if not nick in self.registryValue('relaybots'):
            return
        try:
            msg.nick = re.match(r"^\[(.*)\]", text).groups(1)[0]
        except AttributeError:
            pass

    def doPrivmsg(self, irc, msg):
        self.do_privmsg_notice(irc, msg)


Class = ArchLinuxCN


class not_in_offical(Exception):
    '''This package is not in official repoisitories'''
    pass


class not_found_in_offical(Exception):
    '''This keywoard is not found in official repoisitories'''
    pass


class not_in_archlinuxcn(Exception):
    '''This package is not in official repoisitories'''
    pass


class not_found_in_archlinuxcn(Exception):
    '''This keywoard is not found in official repoisitories'''
    pass


class not_in_aur(Exception):
    '''This package is not in AUR'''
    pass


class not_found_in_aur(Exception):
    '''This  keywoard is not found in AUR'''
    pass


class Repository:
    '''Represents a Arch Linux software repository.'''

    def __init__(self, find_url, search_url=None):
        self.find_url = find_url
        self.search_url = search_url

    def find(self, pkgname):
        '''Find a package in repository.'''
        try:
            package = requests.get(self.find_url.format(pkgname)).json()['results'][0]
        except IndexError:
            return -1


offical = Repository(find_url="https://www.archlinux.org/packages/search/json/?name={}&arch=any&arch=x86_64",
                     search_url="https://www.archlinux.org/packages/search/json/?q={}&arch=any&arch=x86_64")
aur = Repository(find_url="https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={}",
                 search_url="https://aur.archlinux.org/rpc/?v=5&type=search&by=name-desc&arg={}")


# May I use one function to union these find functions in the future?

def official_package(pkgname):
    '''Find a Arch Linux Package exactly through web interface.'''
    url = "https://www.archlinux.org/packages/search/json/?name={}&arch=any&arch=x86_64"
    try:
        package = requests.get(url.format(pkgname)).json()['results'][0]
    except IndexError:
        raise not_in_offical()
    else:
        return package


def aurweb(package):
    '''Find a AUR Package exactly through AURWeb.'''
    url = "https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={}"
    try:
        package = requests.get(url.format(package)).json()['results'][0]
    except IndexError:
        raise not_in_aur()
    else:
        return package


def archlinuxcn_package(package):
    url = "https://build.archlinuxcn.org/api/packages/{}"
    package = requests.get(url.format(package))
    if package.status_code != 200:
        raise not_in_archlinuxcn()
    return package.json()['latest']


def archlinuxcn_package_text(package):
    source = "https://github.com/archlinuxcn/repo/tree/master/{package}"
    template = "{package}({pkgver}) is build {status} on {time}.\nView source on {source_url}"
    text = template.format(package=package['pkgname'],
                           pkgver=package['pkgver'],
                           status="passed" if package['building_ok'] else "failed",
                           time=package['latest_build_time'],
                           source_url=source.format(package=package['pkgname']))
    return text.split("\n")


def search_official_package(keyword):
    '''Search official packages.'''
    url = "https://www.archlinux.org/packages/search/json/?q={}&arch=any&arch=x86_64"
    query = requests.get(url.format(keyword)).json()['results']
    try:
        pkgnames = query[:5]
    except IndexError:
        pkgnames = query
    finally:
        if not pkgnames:
            raise not_found_in_offical()
        else:
            return [pkg['pkgname'] for pkg in pkgnames]


def search_aur_package(keyword):
    '''Search AUR packages.'''
    url = "https://aur.archlinux.org/rpc/?v=5&type=search&by=name-desc&arg={}"
    query = requests.get(url.format(keyword)).json()['results']
    try:
        pkgnames = query[:5]
    except IndexError:
        pkgnames = query
    finally:
        if not pkgnames:
            raise not_found_in_aur()
        else:
            return [pkg['Name'] for pkg in pkgnames]


def official_package_text(package):
    '''Make message text though json.'''
    pkgname = package['pkgname']
    pkgdesc = package['pkgdesc']
    pkgarch = package['arch']
    pkgver = package['pkgver'] + '-' + package['pkgrel']
    flag_date = package['flag_date']
    repo = package['repo']
    pkgurl = "https://www.archlinux.org/packages/{}/{}/{}/".format(
        repo, pkgarch, pkgname)
    template = "[{}/{}] ({}),version {} {}. \nMore information on website: {}"
    text = template.format(repo,
                           pkgname,
                           pkgdesc,
                           pkgver,
                           (",flagged out of date on {}".format(
                               flag_date) if flag_date else ""),
                           pkgurl)
    return text.split("\n")


def aurweb_text(package):
    '''Make message text though json.'''
    pkgname = package['Name']
    pkgdesc = package['Description']
    pkgver = package['Version']
    maintainer = package['Maintainer']
    pkgurl = "https://aur.archlinux.org/packages/{}/".format(pkgname)
    template = "[AUR] {} ({}),version {} ,maintained by {}. \n More information on website: {}"
    text = template.format(pkgname,
                           pkgdesc,
                           pkgver,
                           maintainer,
                           pkgurl)
    return text.split("\n")

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
