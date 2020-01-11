###
# Copyright (c) 2003-2005, Jeremiah Fincher
# Copyright (c) 2010, James McCoy
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

import ast
import re
import random


import supybot.utils as utils
import supybot.commands
import supybot.ircmsgs as ircmsgs
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring
_ = PluginInternationalization('Monologue')


class Monologue(callbacks.Plugin):
    """This plugin provides some small Monologue like (Russian) roulette,
    eightball, monologue, coin and dice."""

    @supybot.commands.wrap(['anything'])
    def coin(self, irc, msg, args):
        """takes no arguments

        Flips a coin and returns the result.
        """
        if random.randrange(0, 2):
            irc.reply(_('heads'))
        else:
            irc.reply(_('tails'))

    @supybot.commands.wrap(['anything'])
    def roll(self, irc, msg, args, m):
        """<dice>d<sides><expression>

        Rolls <dice> dice(s) with <sides> number of sides <dice> times. 
        And execute some expression for result.
        For example, 2d6 will roll 2 six-sided dice; 10d10 will roll 10
        ten-sided dice.
        """

        roll_re = re.compile(r'(\d+)?d(\d+)')

        try:
            selection = re.search(roll_re,m)
            assert selection
        except AssertionError:
            irc.error(_("Dice must be of the form [dice]d<sides>[expression]"))

        (dice, sides) = [ int(x or 1) for x in selection.groups() ]        
    
        expression = re.split(roll_re,m)[-1]

        try:
            assert (dice>0 and dice<100 and sides>0 and sides<100)
        except AssertionError:
            irc.error(_("Inappropriate dice or sides. (0<dice<100, 0<sides<100)"))
        else:
            L = [0] * dice
            for i in range(dice):
                L[i] = random.randrange(1, sides+1)
        
            if expression:
                try:
                    dices = f"[{format('%L', [str(x) for x in L])}]"
                    result = eval(str(sum(L))+expression)
                    irc.reply(f"{dices}{expression} = {result}")
                except (ValueError,NameError) as err:
                    irc.reply(f"Expression execute failed:{str(err)}")
            else:
                irc.reply(format('%L', [str(x) for x in L]))

Class = Monologue


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
