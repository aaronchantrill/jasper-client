# -*- coding: utf-8 -*-
import os.path
import pdb
import textPlayer as tp
from jasper import app_utils
from jasper import plugin

class FrotzPlugin(plugin.SpeechHandlerPlugin):
    def get_phrases(self):
        return [
            self.gettext("BEGIN SIMULATION ZORK ONE"),
            self.gettext("BEGIN SIMULATION MIND FOREVER VOYAGING"),
            self.gettext("BEGIN SIMULATION HITCHHIKERS GUIDE"),
            self.gettext("BEGIN SIMULATION")
            ]
    
    def handle(self,text,mic,*args):
        self._mic=mic
        if( args ):
            self._conversation=args[0]
            self._logger=self._conversation._logger
        else:
            self._logger = logging.getLogger(__name__)
        #pdb.set_trace()
        self.game_file="zork1.z5"
        self.game_name="zork one"
        if( "A MIND FOREVER VOYAGING" in text ):
            self.game_file="AMFV.z5"
            self.game_name="a mind forever voyaging"
        if( "HITCHHIKERS" in text ):
            self.game_file="hhgg.z3"
            self.game_name="the hitchhiker's guide to the galaxy"
        self.game=self.game_file[:self.game_file.find('.')]
        self.savefile=os.path.join(os.path.dirname(os.path.realpath(__file__)),"games",self.game+".sav")
        self._mic.say(self.gettext("beginning simulation "+self.game_name))
        #active_stt_slug = conversation.config['stt_engine']
        #frotz_stt_plugin_info = conversation.application.plugins.get_plugin(active_stt_slug, category='stt')
        #frotz_stt_plugin = frotz_stt_plugin_info.plugin_class('default', self.brain.get_plugin_phrases(), frotz_stt_plugin_info,conversation.config)

        #while( True ):
        #    text=frotz_listen()
        #    print( text )
        #    if( text==["END SIMULATION"] ):
        #        break
        #    mic.say(str(text))
        
        # open zork1.corpus in the current directory and create a phrase list from it
        corpus = os.path.join(os.path.dirname(os.path.realpath(__file__)),"games",self.game+".corpus")
        phrases=['END SIMULATION']
        with open(corpus, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                phrases.append(line)

        self._logger.debug('Starting frotz mode...')
        with self._mic.special_mode(self.game, phrases):
            self._logger.debug('Frotz mode started.')
            t = tp.textPlayer(self.game_file)
            response = t.run()
            if( os.path.isfile(self.savefile)):
                t.restore(self.savefile)
                response = t.execute_command('l')
            current_location=response.location
            self._mic.say(response.location)
            if( response.description ):
                self._mic.say(response.description)
            
            mode_not_stopped = True
            while mode_not_stopped:
                texts = self._mic.active_listen(indicator=0)

                text = ''
                if texts:
                    text = ', '.join(texts).upper()

                if not text:
                    #mic.say(_('Pardon?'))
                    continue
                
                # Here I have the chance to catch some commonly misheard phrases
                if( "GO SELF" in text ):
                    self._logger.debug('GO SELF corrected to GO SOUTH')
                    text="GO SOUTH"
                if( "WHERE ROBE" in text ):
                    self._logger.debug('WHERE ROBE corrected to WEAR ROBE')
                    text="WEAR ROBE"

                if( "END SIMULATION" in text ):
                    mode_not_stopped = False
                else:
                    response = t.execute_command(text)
                    say_location=False
                    # You don't have to state the location at the beginning of each response
                    # For the most part, I only need a location update when the location changes
                    # or if I ask for "look" or "where am i"
                    if( current_location!=response.location ):
                        current_location=response.location
                        say_location=True
                    if( text==['LOOK'] or text==['WHERE AM I'] ):
                        say_location=True
                    if( not response.description ):
                        say_location=True
                    if( say_location ):
                        self._mic.say(response.location)
                    if( response.description ):
                        self._mic.say(response.description)

        self._mic.say(self.gettext('Saving simulation'))
        t.save(self.savefile)
        t.quit()
        self._mic.say(self.gettext('Ending simulation'))
        self._logger.debug("Frotz mode stopped.")

    # Originally I thought I would have to implement my own version of listen() in order to change
    # the language model/dictionary in use. Then I figured out how to use the mic_special_mode to
    # accomplish this. So this is vestigial, but I'm not quite ready to get rid of it yet.
    def frotz_listen(self, timeout=3):
        # record until <timeout> second of silence or double <timeout>.
        n = int(round((self._mic._input_rate/self._mic._input_chunksize)*timeout))
        frames = []
        for frame in self._input_device.record(self._mic._input_chunksize,
                                               self._mic._input_bits,
                                               self._mic._input_channels,
                                               self._mic._input_rate):
            frames.append(frame)
            if len(frames) >= 2*n or (
                    len(frames) > n and self._snr(frames[-n:]) <= 3):
                break
        with self._mic._write_frames_to_file(frames) as f:
            return self.frotz_stt_engine.transcribe(f)
    
    def is_valid(self, text):
        """
        Returns True if the input is related to jokes/humor.

        Arguments:
        text -- user-input, typically transcribed speech
        """
        return any(p.lower() in text.lower() for p in self.get_phrases())
