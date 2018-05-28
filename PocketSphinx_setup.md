# PocketSphinx setup
## These instructions are for installing pocketsphinx on Debian 9 (Stretch). I will also test on Raspbian Stretch and update this message when finished.

`sudo apt install alsa-utils`

## test the microphone ("hello, can you hear me?")
```
alsamixer
arecord -vv -r16000 -fS16_LE -c1 -d3 test.wav
```
# Install PocketSphinx
## Install openfst:
```
sudo apt install gcc g++ make python-pip autoconf libtool
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
```
sudo apt install git gfortran autoconf-archive
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
```
git clone https://github.com/AdolfVonKleist/Phonetisaurus.git
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
```
sudo apt install swig libasound2-dev bison
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
```
git clone https://github.com/cmusphinx/pocketsphinx.git
cd pocketsphinx
./autogen.sh
./configure
make
sudo make install
cd
which pocketsphinx_continuous
```
## Install python PocketSphinx libary
### Convert to .whl 
```
wget https://pypi.python.org/packages/e1/e8/448fb4ab687ecad1be8708d152eb7ed69455be7740fc5899255be2228b52/pocketsphinx-0.1.3-py2.7-linux-x86_64.egg#md5=1b4ce66e44f53d23c981e789f84edf29`
wget https://pypi.python.org/packages/0c/80/16a85b47702a1f47a63c104c91abdd0a6704ee8ae3b4ce4afc49bc39f9d9/wheel-0.30.0-py2.py3-none-any.whl#md5=1d61793f816d6b60513364fe2de9c1b3
python ./wheel-0.30.0-py2.py3-none-any.whl/wheel convert pocketsphinx-0.1.3-py2.7-linux-x86_64.egg
pip install ./pocketsphinx-0.1.3-cp27-none-linux_x86_64.whl
```
## Install the general english language model files:
`sudo apt install pocketsphinx-en-us`

## Install CMUCLMTK
```
sudo apt install subversion
svn co https://svn.code.sf.net/p/cmusphinx/code/trunk/cmuclmtk/
cd cmuclmtk
./autogen.sh
make
sudo make install
sudo ldconfig
cd
sudo pip install cmuclmtk
```
## Get the CMUDict
```
mkdir CMUDict
cd CMUDict
wget https://raw.githubusercontent.com/cmusphinx/cmudict/master/cmudict.dict
cat cmudict.dict | perl -pe 's/([0-9]+)//;s/\s+/ /g;s/^\s+//;s/\s+$//; @_=split(/\s+/); $w=shift(@_);$_=$w."\t".join(" ",@_)."\n";' > cmudict.formatted.dict
phonetisaurus-train --lexicon cmudict.formatted.dict --seq2_del
```
## Test:
```
vi test_reference.txt
<s> hello can you hear me </s>
```
### Create test.vocab
```
text2wfreq < test_reference.txt | wfreq2vocab > test.vocab
```
### Create test.idngram
```
text2idngram -vocab test.vocab -idngram test.idngram < test_reference.txt
```
### Create test.lm
```
idngram2lm -vocab_type 0 -idngram test.idngram -vocab test.vocab -arpa test.lm
```
### Create test.formatted.dict
```
phonetisaurus-g2pfst --model=/home/jasper/CMUDict/train/model.fst --nbest=1 --beam=1000 --thresh=99.0 --accumulate=true --pmass=0.85 --nlog_probs=false --wordlist=./test.vocab > test.dict
cat test.dict | sed -rne '/^([[:lower:]])+\s/p' | perl -pe 's/([0-9])+//g;s/\s+/ /g;@_=split(/\s+/);$w=shift(@_);$_=$w."\t".join(" ",@_)."\n";' > test.formatted.dict
```
## Test with audio file:
`pocketsphinx_continuous -hmm /usr/share/pocketsphinx/model/en-us/en-us -lm ./test.lm -dict ./test.formatted.dict -samprate 16000/8000/48000 -infile test.wav 2>/dev/null`

## Test with microphone:
`pocketsphinx_continuous -hmm /usr/share/pocketsphinx/model/en-us/en-us -lm ./test.lm -dict ./test.formatted.dict -samprate 16000/8000/48000 -inmic yes 2>/dev/null`
