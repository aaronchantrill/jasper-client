# -*- coding: utf-8 -*-
import random
from jasper import plugin


class MeaningOfLifePlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("THE ULTIMATE ANSWER"),
            self.gettext("MEANING OF LIFE")
                ]

    def handle(self, text, mic, *args):
        """
        Responds to user-input, typically speech text, by relaying the
        meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        if( "THE ULTIMATE ANSWER" in text ):
            message = [ self.gettext( "Fourty two" ) ]
        else:
            message = [ self.gettext("Well, it's nothing very special. Try and be nice to people, avoid eating fat, reed a good book every now and then, get some walking in, and try and live together in peace and harmony with people of all creeds and nations.") ]

        mic.say(message)

    def is_valid(self, text):
        """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
