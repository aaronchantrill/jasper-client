# -*- coding: utf-8 -*-
import random
from jasper import plugin


class ThanksPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("THANKS"),
            self.gettext("THANK YOU")
                ]

    def handle(self, text, mic, *args):
        """
        Responds to user-input, typically "thank you" with "You are welcome"

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        """
        messages = ["You're welcome","You are welcome","It's all part of the job"]
        message = random.choice(messages)

        mic.say(message)

    def is_valid(self, text):
        """
        Returns True if the input is a thank you message

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
