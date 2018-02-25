# -*- coding: utf-8 -*-
import datetime
from jasper import app_utils
from jasper import plugin
from pytz import timezone

class ClockPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("TIME"),
            self.gettext("WHAT TIME IS IT IN WEST VIRGINIA"),
            self.gettext("WHAT TIME IS IT IN HAWAII"),
            self.gettext("WHAT TIME IS IT IN VIRGINIA")
                ]

    """Given an int32 number, print it in English."""
    def int_to_en(self,num):
        d = { 0 : 'zero', 1 : 'one', 2 : 'two', 3 : 'three', 4 : 'four', 5 : 'five',
              6 : 'six', 7 : 'seven', 8 : 'eight', 9 : 'nine', 10 : 'ten',
              11 : 'eleven', 12 : 'twelve', 13 : 'thirteen', 14 : 'fourteen',
              15 : 'fifteen', 16 : 'sixteen', 17 : 'seventeen', 18 : 'eighteen',
              19 : 'nineteen', 20 : 'twenty',
              30 : 'thirty', 40 : 'forty', 50 : 'fifty', 60 : 'sixty',
              70 : 'seventy', 80 : 'eighty', 90 : 'ninety' }
        k = 1000
        m = k * 1000
        b = m * 1000
        t = b * 1000
    
        assert(0 <= num)
    
        if (num < 20):
            return d[num]
    
        if (num < 100):
            if num % 10 == 0: return d[num]
            else: return d[num // 10 * 10] + '-' + d[num % 10]
    
        if (num < k):
            if num % 100 == 0: return d[num // 100] + ' hundred'
            else: return d[num // 100] + ' hundred and ' + int_to_en(num % 100)
    
        if (num < m):
            if num % k == 0: return int_to_en(num // k) + ' thousand'
            else: return int_to_en(num // k) + ' thousand, ' + int_to_en(num % k)
    
        if (num < b):
            if (num % m) == 0: return int_to_en(num // m) + ' million'
            else: return int_to_en(num // m) + ' million, ' + int_to_en(num % m)
    
        if (num < t):
            if (num % b) == 0: return int_to_en(num // b) + ' billion'
            else: return int_to_en(num // b) + ' billion, ' + int_to_en(num % b)
    
        if (num % t == 0): return int_to_en(num // t) + ' trillion'
        else: return int_to_en(num // t) + ' trillion, ' + int_to_en(num % t)
    
        raise AssertionError('num is too large: %s' % str(num))
    
    def handle(self, text, mic, *args):
        """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        
        """
        Check if the user is asking for time in a specific place
        places include:
           West Virginia (tz=America/New_York)
           Virginia (tz=America/New_York)
           Hawaii (tz=Pacific/Honolulu)
        """
        where=""
        if "west virginia" in text.lower():
            tz=timezone("America/New_York")
            where=" in West Virginia"
        elif "virginia" in text.lower():
            tz=timezone("America/New_York")
            where=" in Virginia"
        elif "hawaii" in text.lower():
            tz=timezone("Pacific/Honolulu")
            where=" in Hawaii"
        else:
            tz = app_utils.get_timezone(self.profile)
        now = datetime.datetime.now(tz=tz)
        #if( self.config['language']=='en-US' ):
        if(1):
            currentHour=now.hour
            ap="Aye-Em"
            if( currentHour>11 ):
                currentHour=currentHour-12
                ap="Pee-Em"
            if( currentHour==0 ):
                currentHour=12
            writtenHour=self.int_to_en(currentHour)
            writtenMinute=self.int_to_en(now.minute)
            if now.minute == 0:
                fmt = "It is "+writtenHour+" "+ap+" right now"+where+"."
            elif now.minute < 10:
                fmt = "It is "+writtenHour+" oh "+writtenMinute+" "+ap+" right now"+where+"."
            else:
                fmt = "It is "+writtenHour+" "+writtenMinute+" "+ap+" right now"+where+"."
            mic.say(self.gettext(fmt).format(t=now))
        else:
            if now.minute == 0:
                fmt = "It is {t:%l} {t:%P} right now."
            else:
                fmt = "It is {t:%l}:{t.minute} {t:%P} right now."
            mic.say(self.gettext(fmt).format(t=now))

    def is_valid(self, text):
        """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
