# -*- coding: utf-8 -*-
import audioop
import collections
import contextlib
import logging
import math
import os
import sqlite3
import sys
import tempfile
import threading
import wave

from datetime import datetime
from . import paths

if sys.version_info < (3, 0):  # NOQA
    import Queue as queue
else:  # NOQA
    import queue

from . import alteration
from . import paths


def get_config_value(config, name, default):
    logger = logging.getLogger(__name__)
    try:
        value = int(config['audio'][name])
    except KeyError:
        logger.debug('%s not configured, using default.', name)
        value = None
    except ValueError:
        logger.debug('%s is not an integer, using default.', name)
        value = None
    return value if value else default


class Mic(object):
    """
    The Mic class handles all interactions with the microphone and speaker.
    """

    def __init__(self, input_device, output_device,
                 passive_stt_engine, active_stt_engine,
                 tts_engine, config, keyword='JASPER'):
        self._logger = logging.getLogger(__name__)
        self._keyword = keyword
        self.tts_engine = tts_engine
        self.passive_stt_engine = passive_stt_engine
        self.active_stt_engine = active_stt_engine
        self._input_device = input_device
        self._output_device = output_device

        self._input_rate = get_config_value(config, 'input_samplerate', 16000)
        self._input_bits = get_config_value(config, 'input_samplewidth', 16)
        self._input_channels = get_config_value(config, 'input_channels', 1)
        self._input_chunksize = get_config_value(config, 'input_chunksize',1024)
        self._output_chunksize = get_config_value(config, 'output_chunksize',1024)
        
        # Save active input for inspection?
        # (active input is after the 'wake word' has been detected, so it is more likely that the speaker knows they are addressing Jasper)
        self._save_active_input=False
        try:
            self._save_active_input=config["save_active_input"]
        except KeyError:
            try:
                self._save_active_input=config["save_input"]
            except KeyError:
                self._save_active_input=False
            self._logger.debug("self._save_active_input=%s"%str(self._save_active_input))

        # Save passive input for inspection?
        # (passive input is before the 'wake word' has been detected, so it is likely to pick up random conversation)
        self._save_passive_input=False
        try:
            self._save_passive_input=config["save_passive_input"]
        except KeyError:
            try:
                self._save_passive_input=config["save_input"]
            except KeyError:
                self._save_passive_input=False
        
        # Noise is input with no words detected. Likely to pick up random conversation and noises in the house.
        self._save_noise=False
        try:
            self._save_noise=config["save_noise"]
        except KeyError:
            try:
                self._save_noise=config["save_noise"]
            except KeyError:
                self._save_noise=False
            
        if( self._save_active_input or self._save_passive_input or self._save_noise ):
            self._audiolog=os.path.join(paths.CONFIG_PATH,"audiolog")
            self._audiolog_db=os.path.join(self._audiolog,"audiolog.db")
            self._logger.info("Checking audio log directory %s"%self._audiolog)
            if not os.path.exists(self._audiolog):
                self._logger.info("Creating audio log directory %s"%self._audiolog)
                os.makedirs(self._audiolog)
            self._conn=sqlite3.connect(self._audiolog_db)
        
        # save a canned response. We will be saying "yes" a lot, no need to encode it each time.
        self._yes=tempfile.SpooledTemporaryFile()
        self._yes.write(self.tts_engine.say("yes"))
        try:
            output_padding = config['audio']['output_padding']
        except KeyError:
            self._logger.debug('output_padding not configured,' +
                               'using default.')
            output_padding = None
        if output_padding and output_padding.lower() in ('true', 'yes', 'on'):
            self._output_padding = True
        else:
            self._output_padding = False

        self._logger.debug('Input sample rate: %d Hz', self._input_rate)
        self._logger.debug('Input sample width: %d bit', self._input_bits)
        self._logger.debug('Input channels: %d', self._input_channels)
        self._logger.debug('Input chunksize: %d frames', self._input_chunksize)
        self._logger.debug('Output chunksize: %d frames', self._output_chunksize)
        self._logger.debug('Output padding: %s', 'yes' if self._output_padding else 'no')

        self._threshold = 2.0**self._input_bits
        self._transcribed = ""

    @contextlib.contextmanager
    def special_mode(self, name, phrases):
        plugin_info = self.active_stt_engine.info
        plugin_config = self.active_stt_engine.profile

        original_stt_engine = self.active_stt_engine

        try:
            mode_stt_engine = plugin_info.plugin_class(name, phrases, plugin_info, plugin_config)
            self.active_stt_engine = mode_stt_engine
            yield
        finally:
            self.active_stt_engine = original_stt_engine

    # Return the root mean square of the signal intensity.
    def _snr(self, frames):
        rms = audioop.rms(b''.join(frames), int(self._input_bits/8))
        if rms > 0 and self._threshold > 0:
            return 20.0 * math.log(rms/self._threshold, 10)
        else:
            return 0
    
    # Copies a file pointed to by a file pointer to a permanent file for training purposes
    def _log_audio(self, fp, transcription, sample_type="unknown"):
        if(( sample_type.lower()=="noise" and self._save_noise )or( sample_type.lower()=="passive" and self._save_passive_input )or( sample_type.lower()=="active" and self._save_active_input )):
            fp.seek(0)
            filename="%s_%s.wav"%( datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),sample_type )
            f=open(os.path.join(self._audiolog,filename),"w")
            f.write(fp.read())
            f.close()
            # Also add a line to the sqlite database
            c=self._conn.cursor()
            c.execute('''create table if not exists audiolog(datetime,filename,type,transcription,verified_transcription,speaker,reviewed)''')
            self._conn.commit()
            c.execute( '''insert into audiolog values(?,?,?,?,'','','')''',(datetime.now().strftime('%Y-%m-%d %H-%i-%s'),filename,sample_type,transcription) )
            self._conn.commit()
        
    @contextlib.contextmanager
    def _write_frames_to_file(self, frames):
        with tempfile.NamedTemporaryFile(mode='w+b') as f:
            wav_fp = wave.open(f, 'wb')
            wav_fp.setnchannels(self._input_channels)
            wav_fp.setsampwidth(int(self._input_bits/8))
            wav_fp.setframerate(16000)
            if self._input_rate == 16000:
                wav_fp.writeframes(''.join(frames))
            else:
                wav_fp.writeframes(
                    audioop.ratecv(
                        ''.join(frames),
                        int(self._input_bits/8),
                        self._input_channels,
                        self._input_rate,
                        16000,
                        None
                    )[0]
                )
            wav_fp.close()
            f.seek(0)
            yield f

    def check_for_keyword(self, frame_queue, keyword_uttered, keyword):
        while True:
            frames = frame_queue.get()
            with self._write_frames_to_file(frames) as f:
                try:
                    self._transcribed = self.passive_stt_engine.transcribe(f)
                except:
                    dbg = (self._logger.getEffectiveLevel() == logging.DEBUG)
                    self._logger.error("Transcription failed!", exc_info=dbg)
                else:
                    if self._transcribed and any([keyword.lower() in t.lower() for t in self._transcribed if t]):
                        keyword_uttered.set()
                finally:
                    frame_queue.task_done()

    def wait_for_keyword(self, keyword=None):
        if not keyword:
            keyword = self._keyword
        frame_queue = queue.Queue()
        keyword_uttered = threading.Event()

        # FIXME: not configurable yet
        num_worker_threads = 2

        for i in range(num_worker_threads):
            t = threading.Thread(target=self.check_for_keyword,args=(frame_queue, keyword_uttered, keyword))
            t.daemon = True
            t.start()

        frames = collections.deque([], 30)
        recording = False
        recording_frames = []
        self._logger.info("Waiting for keyword '%s'...", keyword)
        for frame in self._input_device.record(self._input_chunksize,
                                               self._input_bits,
                                               self._input_channels,
                                               self._input_rate):
            if keyword_uttered.is_set():
                if self._logger.isEnabledFor(logging.DEBUG):
                    self._logger.info("Keyword %s has been uttered", keyword)
                return self._transcribed
            frames.append(frame)
            if not recording:
                snr = self._snr([frame])
                if snr >= 10:  # 10dB
                    # Loudness is higher than normal, start recording and use
                    # the last 10 frames to start
                    self._logger.debug("Started recording on device '%s'",
                                       self._input_device.slug)
                    self._logger.debug("Triggered on SNR of %sdB", snr)
                    recording = True
                    recording_frames = list(frames)[-10:]
                elif len(frames) >= frames.maxlen:
                    # Threshold SNR not reached. Update threshold with
                    # background noise.
                    self._threshold = float(audioop.rms("".join(frames), 2))
            else:
                # We're recording
                recording_frames.append(frame)
                if len(recording_frames) > 20:
                    # If we recorded at least 20 frames, check if we're below
                    # threshold again
                    last_snr = self._snr(recording_frames[-10:])
                    self._logger.debug(
                        "Recording's SNR dB: %f", last_snr)
                    if last_snr <= 3 or len(recording_frames) >= 60:
                        # The loudness of the sound is not at least as high as
                        # the the threshold, or we've been waiting too long
                        # we'll stop recording now
                        recording = False
                        self._logger.debug("Recorded %d frames",
                                           len(recording_frames))
                        frame_queue.put(tuple(recording_frames))
                        self._threshold = float(
                            audioop.rms(b"".join(frames), 2))

    #def listen(self):
    #    # The way this appears to work is that it starts in passive mode and continually grabs small sections of audio and
    #    # checks to see if that contains the "wake word". Right now I am checking for all the action words at the same time,
    #    # then passing that transcription to the intent parser to figure out what to do. It seems like it captures a second
    #    # or so after it hears the wake word, so that seems to work okay, even when the wake word is the first word spoken.
    #    #
    #    # This makes perfect sense when you are processing the wake word locally and sending the full text parsing out, but
    #    # I am keeping all the parsing local so I don't really have to do that.
    #    #
    #    # What I really want to be doing is have the microphone continually checking for audio above a certain threshold
    #    # (really I want it to be listening for audio in the vocal range, but I think checking for volume level is the best 
    #    # I can do at the moment). Then 
    #    response=self.wait_for_keyword(self._keyword)
    #    # What I really want to do here is check to see if there is a speechhandler plugin keyword
    #    # here. If so, handle it, if not then start actively listening.
    #    # Brain.query(texts) seems like an obvious choice here, but I'm not sure how to get back to brain from here.
    #    if(( response == [self._keyword.upper()] )or( response == ["GUIDE "+self._keyword.upper()] )):
    #        response=self.active_listen()
    #    # if the response contains more than just the wake word, then skip the active listen and just process the result
    #    self._logger.debug( "<< "+str(response) )
    #    return response

    # I am making listen() just a wrapper around active_listen(). The main difference between listen() and active_listen()
    # is that listen() requires the wakeword by default, whereas active_listen() does not.
    def listen(self):
        return self.active_listen(indicator=0, timeout=3, require_wakeword=1)

    def active_listen(self, indicator=1, timeout=.5, require_wakeword=0):
        self._logger.info("active listen")
        # start with not recording
        recording=False
        # The volume threshold was originally set to 3, which would be very loud in my case, and the volume would never fall below that.
        volume_threshold=-40
        # record until <timeout> second of silence or double <timeout>.
        n = int(round((self._input_rate/self._input_chunksize)*timeout))
        if( indicator ):
            # self.play_file(paths.data('audio', 'beep_hi.wav'))
            self._yes.seek(0)
            self._output_device.play_fp(self._yes)
        frames = []
        for frame in self._input_device.record(self._input_chunksize,
                                               self._input_bits,
                                               self._input_channels,
                                               self._input_rate):
            frames.append(frame)
            if( len(frames)>4 ):
                volume=self._snr(frames[-n:])
                self._logger.info( "volume=%d"%volume) )            
                if( volume>volume_threshold and not recording ):
                    recording=True
                    if( len(frames)>n ):
                        frames=frames[-n:]
                if( recording ):
                    self._logger.info( "frames=%d of %d"%(len(frames),2*n) )
                    # I don't know where 3 comes from. In my case, a value of -40 would seem to make more sense
                    # (by experiment, I'm not sure exactly what this number represents or how it is calculated)
                    # It would probably make sense to figure this out from the background noise levels in the 
                    # environment.
                    #if len(frames) >= 2*n or (len(frames) > n and self._snr(frames[-n:]) <= 3):
                    # Also, this is an average of all samples. Seems like we should only use the last second or so
                    if( len(frames) > 2*n and self._snr(frames[-n:])<=volume_threshold ):
                        self._logger.debug("max length=%d"%(2*n))
                        self._logger.debug("frames length=%d"%len(frames))
                        break
        # self.play_file(paths.data('audio', 'beep_lo.wav'))
        with self._write_frames_to_file(frames) as f:
            if( require_wakeword ):
                # if we are waiting for a wake word, use the passive stt engine first (much faster than the active stt engine)
                presponse=self.passive_stt_engine.transcribe(f)
                self._logger.info("passive response: %r"%presponse)
                if( len(presponse)==0 ):
                    # this is noise, no identifiable voices
                    self._log_audio(f,"","noise")
                else:
                    keyword_spoken=any([self._keyword.lower() in t.lower() for t in presponse if t])
                    self._logger.debug( str(keyword_spoken) )
                    if( any([self._keyword.lower() in t.lower() for t in presponse if t]) ):
                        self.play_file(paths.data('audio', 'beep_lo.wav'))
                        presponse=self.active_stt_engine.transcribe(f)
                        if( len(presponse) ):
                            self._log_audio(f,str(presponse),"active")
                    else:
                        if( len(presponse) ):
                            self._log_audio(f,str(presponse),"passive")
                            # clear presponse so we don't trigger anything in conversation
                            presponse=[]
            else:
                # if we are not waiting for a wake word, go ahead and use the active engine.
                # it would be good to have some way of 
                presponse=self.active_stt_engine.transcribe(f)
                if( len(presponse) ):
                    self._log_audio(f,str(presponse),"active")
        #if( self._save_input and not transcribed==[''] ):
        #    self._filecount+=1
        #    f=open(os.path.join(self._audiolog,"%d_%s.wav"%(self._filecount,text)),"w")
        #    f.write(fp.read())
        #    f.close()
            return presponse

    # Output methods
    def play_file(self, filename):
        self._output_device.play_file(filename,chunksize=self._output_chunksize,add_padding=self._output_padding)

    def say(self, phrase):
        print("<< %s"%phrase)
        altered_phrase = alteration.clean(phrase)
        with tempfile.SpooledTemporaryFile() as f:
            f.write(self.tts_engine.say(altered_phrase))
            f.seek(0)
            self._output_device.play_fp(f)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("stt").setLevel(logging.WARNING)
    audio = Mic.get_instance()
    while True:
        text = audio.listen()[0]
        if text:
            audio.say(text)
