# -*- coding: utf-8 -*-
import logging
import pdb
from . import paths
from . import i18n
#  from notifier import Notifier


class Conversation(i18n.GettextMixin):
    def __init__(self, application):
        translations = i18n.parse_translations(paths.data('locale'))
        i18n.GettextMixin.__init__(self, translations, application.config)
        self._logger = logging.getLogger(__name__)
        self.application = application
        self.mic = application.mic
        self.profile = application.config
        self.brain = application.brain
        self.translations = {

        }
        #  self.notifier = Notifier(profile)

    def greet(self):
        # cute, but you don't know who is around to address the system.
        # you also don't really care. If speaker recognition can be added
        # this might make some sense, but since this is the first utterance
        # probably not.
        if False and 'first_name' in self.profile:
            salutation = (self.gettext("How can I be of service, %s?")
                          % self.profile["first_name"])
        else:
            salutation = self.gettext("How can I help?")
        self.mic.say(salutation)

    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.debug('Starting to handle conversation.')
        while True:
            # Print notifications until empty
            """notifications = self.notifier.get_all_notifications()
            for notif in notifications:
                self._logger.info("Received notification: '%s'", str(notif))"""

            input = self.mic.listen()

            if input:
                plugin, text = self.brain.query(input)
                #pdb.set_trace()
                if plugin and text:
                    try:
                        print( plugin )
                        plugin.handle(text,self.mic,self)
                    except Exception:
                        self._logger.error('Failed to execute module',exc_info=True)
                        self.mic.say(self.gettext("I'm sorry. I had some trouble with that operation. Please try again later."))
                    else:
                        self._logger.debug("Handling of phrase '%s' by module '%s' completed", text,plugin.info.name)
            else:
                self.mic.say(self.gettext("No plugin handled that, not even unclear. Can you repeat that?"))
                #input = self.mic.active_listen()
