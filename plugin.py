###
# Copyright (c) 2013, Stacey Ell
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
from time import time
#from datetime import datetime
from functools import partial
from itertools import imap, takewhile
from supybot.commands import (
    additional,
    world,
    wrap
)
import supybot.utils as utils
#import supybot.plugins as plugins
#import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Countdown')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:  x


def decowrap(*args, **kwargs):
    def decorator(func):
        return wrap(func, *args, **kwargs)
    return decorator


def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def modfib():
    fibiter = fib()
    yield next(fibiter)
    next(fibiter)  # skip first `1'
    while True:
        yield next(fibiter)


def countdown_alarm_points(seconds):
    rounder = lambda x: x - (x % 30 if x > 120 else 0)
    alarms = list(imap(rounder, takewhile(lambda x: x < seconds, modfib())))
    alarms.append(seconds)
    return alarms


class Countdown(callbacks.Plugin):
    """Add the help for "@plugin help Countdown" here
    This should describe *how* to use this plugin."""
    def __init__(self, irc, *args, **kwargs):
        self.__parent = super(Countdown, self)
        self.__parent.__init__(irc, *args, **kwargs)
        self.events = {}
        self._restore_events(irc)
        world.flushers.append(self._flush)

    def _restore_events(self, irc):
        pass

    def _flush(self):
        pass

    def die(self):
        self._flush()
        world.flushers.remove(self._flush)
        self.__parent.die()

    def _countdown_resp(self, irc, remaining_seconds, end_response):
        if remaining_seconds > 0:
            irc.reply(utils.timeElapsed(remaining_seconds), prefixNick=False)
        else:
            irc.reply(end_response, prefixNick=False)

    @decowrap(['positiveInt', additional('text')])
    def countdown(self, irc, msg, args, seconds, final_message=None):
        """<seconds> [final_message]

        Counts down
        """
        if final_message is None:
            final_message = 'GO!'
        now = time()
        callback_part = partial(self._countdown_resp, irc)
        for alarm_point in countdown_alarm_points(seconds):
            schedule.addEvent(
                partial(callback_part, alarm_point, final_message),
                now + seconds - alarm_point)


Class = Countdown


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: