This plugin is for playing infocom games with Jasper.

To use it, you should download textPlayer from Daniel Ricks at https://github.com/danielricks/textplayer. Copy all of the .z5 game
files into the games folder. I have already included a modified version of textPlayer.py which does some handy things like split the
location and description into different properties. I've only really worked on Zork1 so far, so your mileage may vary with other
games.

TextPlayer uses a copy of dfrotz, which you have to build. Luckily this is easy and most of the issues have to do with missing shared library files. I found that I needed to install the following on Ubuntu 16.04:

~$ sudo apt install libao-dev libsndfile1 libflac-dev libogg-dev libsndfile1-dev libvorbis-dev pkg-config libmodplug-dev libsamplerate1-dev

You can download dfrotz from github:
~$ git clone https://github.com/DavidGriffith/frotz.git
~$ cd frotz

Then just build with a target of dfrotz. No need to install it, we will just drop it into the same directory with textPlayer.
~/frotz$ make dfrotz
~/frotz$ cp -iv dfrotz ~/jasper-client/plugins/speechhandlers/frotz/

To use this with the Pocketsphinx speech to text engine requires some additional work. First, you will need to extract the games 
commands into a corpus file. For this, I used Zorkword by Mike Threepoint which can be downloaded from 
http://mirror.ifarchive.org/if-archive/infocom/tools/zorkword.zip.

Add the words "end simulation" to the end of the list, otherwise you will be stuck in the game forever with Jasper never being
able to understand your requests to quit.

When running, Jasper often fails to compile the language model so you may want to use the tool at 
http://www.speech.cs.cmu.edu/tools/lmtool-new.html to compile the language model and dictionary from your corpus file, then
just overwrite what Jasper came up with. The language model uses a checksum based on the corpus file, so as long as your
corpus file doesn't change, Jasper won't try to overwrite it.
