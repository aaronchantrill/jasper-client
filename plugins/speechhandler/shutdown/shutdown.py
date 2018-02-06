# -*- coding: utf-8 -*-
import os
from jasper import plugin


class ShutdownPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("SHUT DOWN")
                ]

    def handle(self, text, mic, *args):
        """
        Responds to user-input, typically speech text, by shutting down

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        mic.say('Shutting down')
        os.system('sudo /sbin/shutdown -h now')
        quit()
        
    def is_valid(self, text):
        """
        Returns True if the input is related to the meaning of life.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
