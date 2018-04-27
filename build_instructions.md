# Basic setup
## login as root
```vi /etc/apt/sources.list```
## remove the line that start with "deb cdrom:", save and quit
## apt should already be up to date since we used a network repository
```
apt update
apt install sudo
visudo
adduser jasper
usermod -aG sudo jasper
vi /etc/network/interfaces
```
## This is only for Virtualbox, to create a host-only network so we can ssh into our box. Append
```
allow-hotplug enp0s8
iface enp0s8 inet dhcp
```
## login as vagrant (the account we created while building the box)
## vagrant insecure key
```mkdir -p ~/.ssh
chmod 0700 .ssh
cd .ssh
wget -O ./authorized_keys https://raw.githubusercontent.com/hashicorp/vagrant/master/keys/vagrant.pub
chmod 0600 ./authorized_keys
```
## login as jasper
`sudo apt install avahi-daemon alsa-utils`

## test the microphone ("hello, can you hear me?")
```alsamixer
arecord -vv -fdat /dev/null
arecord -r16000 -fS16_LE -c1 -d3 test.wav
```
# Install PocketSphinx
## Install openfst:
```sudo apt install gcc g++ make python-pip autoconf libtool
wget http://www.openfst.org/twiki/pub/FST/FstDownload/openfst-1.6.7.tar.gz
tar -zxvf openfst-1.6.7.tar.gz
cd openfst-1.6.7
autoreconf -i
./configure --enable-static --enable-shared --enable-far --enable-lookahead-fsts --enable-const-fsts --enable-pdt --enable-ngram-fsts --enable-linear-fsts --prefix=/usr
make
sudo make install
cd
```

## Install mitlm-0.4.2:
```sudo apt install git gfortran autoconf-archive
git clone https://github.com/mitlm/mitlm.git
cd mitlm
vi configure.ac add AC_CONFIG_MACRO_DIRS([m4])
vi Makefile.am  add ACLOCAL_AMFLAGS = -I m4
autoreconf -i
./configure
make
sudo make install
cd
```
## Install Phonetisaurus:
```git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
cd Phonetisaurus
./configure --enable-python
make
sudo make install
cd python
cp -iv ../.libs/Phonetisaurus.so ./
sudo python setup.py install
cd
```
## sphinxbase-0.8:
```sudo apt install swig libasound2-dev bison
git clone https://github.com/cmusphinx/sphinxbase.git
cd sphinxbase
./autogen.sh
./configure 2>&1 |& tee configure.log
grep -i 'alsa' configure.log
make
sudo make install
cd
```
## pocketsphinx-0.8:
```git clone https://github.com/cmusphinx/pocketsphinx.git
cd pocketsphinx
./autogen.sh
./configure
make
sudo make install
cd
which pocketsphinx_continuous
```
## Install python PocketSphinx libary
###Convert to .whl 
```wget https://pypi.python.org/packages/e1/e8/448fb4ab687ecad1be8708d152eb7ed69455be7740fc5899255be2228b52/pocketsphinx-0.1.3-py2.7-linux-x86_64.egg#md5=1b4ce66e44f53d23c981e789f84edf29`
wget https://pypi.python.org/packages/0c/80/16a85b47702a1f47a63c104c91abdd0a6704ee8ae3b4ce4afc49bc39f9d9/wheel-0.30.0-py2.py3-none-any.whl#md5=1d61793f816d6b60513364fe2de9c1b3
python ./wheel-0.30.0-py2.py3-none-any.whl/wheel convert pocketsphinx-0.1.3-py2.7-linux-x86_64.egg
pip install ./pocketsphinx-0.1.3-cp27-none-linux_x86_64.whl
```
## Install the general english language model files:
`sudo apt install pocketsphinx-en-us`

## Install CMUCLMTK
```sudo apt install subversion
svn co https://svn.code.sf.net/p/cmusphinx/code/trunk/cmuclmtk/
cd cmuclmtk
./autogen.sh
make
sudo make install
sudo ldconfig
cd
```
## Get the CMUDict
```mkdir CMUDict
cd CMUDict
wget https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
cat cmudict.dict | perl -pe 's/([0-9]+)//;s/\s+/ /g;s/^\s+//;s/\s+$//; @_=split(/\s+/); $w=shift(@_);$_=$w."\t".join(" ",@_)."\n";' > cmudict.formatted.dict
phonetisaurus-train --lexicon cmudict.formatted.dict --seq2_del
```
## Test:
```vi test_reference.txt
<s> hello can you hear me </s>
Create test.vocab
text2wfreq < test_reference.txt | wfreq2vocab > test.vocab
Create test.idngram
text2idngram -vocab test.vocab -idngram test.idngram < test_reference.txt 
idngram2lm -vocab_type 0 -idngram test.idngram -vocab test.vocab -arpa test.lm
phonetisaurus-g2pfst --model=./train/model.fst --nbest=1 --beam=1000 --thresh=99.0 --accumulate=true --pmass=0.85 --nlog_probs=false --wordlist=./test.vocab > test.dict
cat test.dict | sed -rne '/^([[:lower:]])+\s/p' | perl -pe 's/([0-9])+//g;s/\s+/ /g;@_=split(/\s+/);$w=shift(@_);$_=$w."\t".join(" ",@_)."\n";' > test.formatted.dict
```
## Test with audio file:
`pocketsphinx_continuous -infile test.wav -hmm /usr/share/pocketsphinx/model/en-us/en-us -lm ./CMUDict/test.lm -dict ./CMUDict/test.formatted.dict -samprate 16000/8000/48000 -time yes`

## Test with microphone:
`pocketsphinx_continuous -hmm /usr/share/pocketsphinx/model/en-us/en-us -lm ./test.lm -dict ./test.formatted.dict -samprate 16000/8000/48000 -inmic yes`

# DeepSpeech
```sudo apt install g++ zlib1g-dev openjdk-8-jdk zip unzip
sudo pip install wheel
wget https://github.com/bazelbuild/bazel/releases/download/0.10.0/bazel-0.10.0-without-jdk-installer-linux-x86_64.sh
wget https://github.com/bazelbuild/bazel/releases/download/0.10.0/bazel-0.10.0-without-jdk-installer-linux-x86_64.sh.sha256
sha256sum -c bazel-0.10.0-without-jdk-installer-linux-x86_64.sh.sha256
chmod a+x bazel-0.10.0-without-jdk-installer-linux-x86_64.sh
sudo ./bazel-0.10.0-without-jdk-installer-linux-x86_64.sh
```
## Git Large File Service
```wget https://github.com/git-lfs/git-lfs/releases/download/v2.4.0/git-lfs-linux-amd64-2.4.0.tar.gz
tar -xzvf git-lfs-linux-amd64-2.4.0.tar.gz
cd git-lfs-2.4.0/
sudo ./install.sh
git lfs install
git clone https://github.com/mozilla/tensorflow.git
git clone https://github.com/mozilla/DeepSpeech.git
cd tensorflow
ln -s ../DeepSpeech/native_client/ ./
./configure 
bazel build -c opt --copt=-O3 --copt="-D_GLIBCXX_USE_CXX11_ABI=0" //native_client:libctc_decoder_with_kenlm.so
bazel build --config=monolithic -c opt --copt=-O3 --copt="-D_GLIBCXX_USE_CXX11_ABI=0" --copt=-fvisibility=hidden //native_client:libdeepspeech.so //native_client:deepspeech_utils //native_client:generate_trie
cd ../DeepSpeech/native_client
sudo apt install libsox-dev pkg-config
make deepspeech
PREFIX=/usr/local sudo make install
make bindings
sudo pip install dist/deepspeech*.whl
cd
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz
tar -zxvf deepspeech-0.1.1-models.tar.gz
```
## test deepspeech
`deepspeech models/output_graph.pb models/alphabet.txt models/lm.binary models/trie test.wav`

# Festival:
```sudo apt install festival
sudo apt install festvox-kdlpc16k
sudo apt install festvox-kallpc16k
```
## Mbrola (non-free voices):
```mkdir mbrola
cd mbrola
sudo apt install libc6-i386
wget http://ftp.us.debian.org/debian/pool/non-free/m/mbrola/mbrola_3.01h+2-3+b1_amd64.deb
sudo dpkg -i mbrola_3.01h+2-3+b1_amd64.deb

sudo mkdir /usr/share/festival/voices/english/us1_mbrola/
wget http://festvox.org/packed/festival/1.95/festvox_us1.tar.gz
tar -zxvf festvox_us1.tar.gz
sudo mv -iv festival/lib/voices/english/us1_mbrola/* /usr/share/festival/voices/english/us1_mbrola/
wget http://tcts.fpms.ac.be/synthesis/mbrola/dba/us1/us1-980512.zip
unzip us1-980512.zip
sudo mv -iv us1 /usr/share/festival/voices/english/us1_mbrola/

sudo mkdir /usr/share/festival/voices/english/us2_mbrola/
wget http://festvox.org/packed/festival/1.95/festvox_us2.tar.gz
tar -zxvf festvox_us2.tar.gz
sudo mv -iv festival/lib/voices/english/us2_mbrola/* /usr/share/festival/voices/english/us2_mbrola/
wget http://tcts.fpms.ac.be/synthesis/mbrola/dba/us2/us2-980812.zip
unzip us2-980812.zip
sudo mv -iv us2 /usr/share/festival/voices/english/us2_mbrola/

sudo mkdir /usr/share/festival/voices/english/us3_mbrola/
wget http://festvox.org/packed/festival/1.95/festvox_us3.tar.gz
tar -zxvf festvox_us3.tar.gz
sudo mv -iv festival/lib/voices/english/us3_mbrola/* /usr/share/festival/voices/english/us3_mbrola/
wget http://tcts.fpms.ac.be/synthesis/mbrola/dba/us3/us3-990208.zip
unzip us3-990208.zip
sudo mv -iv us3 /usr/share/festival/voices/english/us3_mbrola/
cd
```
## HTS voices
```mkdir hts_voices
cd hts_voices
wget http://ftp.us.debian.org/debian/pool/main/f/festvox-us-slt-hts/festvox-us-slt-hts_0.2010.10.25-2_all.deb
sudo dpkg -i festvox-us-slt-hts_0.2010.10.25-2_all.deb
cd
```
# install jasper
```sudo apt install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools
sudo pip install pyyaml slugify pytz feedparser mad pyaudio requests

git clone https://github.com/aaronchantrill/jasper-client.git
```
# Create a jasper configuration file
`vi ~/.jasper/profile.yml`
```
location: '98225'
prefers_email: true
#stt_engine: sphinx
#pocketsphinx:
#  #phonetisaurus_executable: 'phonetisaurus-g2p'
#  #fst_model: '/home/drask/Projects/g014b2b/g014b2b.fst'
#  phonetisaurus_executable: 'phonetisaurus-g2pfst'
#  fst_model: '/home/drask/Projects/Phonetisaurus/example/train/model.fst'
#  nbest: 3
stt_engine: deepspeech-stt
deepspeech:
  model: '/home/drask/Projects/DeepSpeech/models/output_graph.pb'
  alphabet: '/home/drask/Projects/DeepSpeech/models/alphabet.txt'
  language_model: '/home/drask/Projects/DeepSpeech/models/lm.binary'
  trie: '/home/drask/Projects/DeepSpeech/models/trie'
  save_input: True
language: en-US
input_device: sysdefault
output_device: sysdefault
timezone: America/Los_Angeles
tts_engine: festival-tts
audio_engine: pyaudio
keyword: Jasper
```
## test jasper
`jasper-client/Jasper.py --debug 2>&1 |& tee jasper.log`

# Build frotz
```git clone https://github.com/DavidGriffith/frotz.git
cd frotz
make dfrotz
cp -iv dfrotz ~/jasper-client/plugins/speechhandler/frotz/
```
# run jasper
`jasper-client/Jasper.py`
