# Tutorial Setup

Thank you for being interested in my workshop! This is a free workshop being presented as part of [Linuxfest Northwest 2018](https://linuxfestnorthwest.org). We have a lot to get through in the course of two hours, so I am asking everyone to arrive with a working development environment and ready to start working.

Jasper is a virtual assistant that runs well on a Raspberry Pi computer. It supports a variety of speech to text and text to speech engines. In this tutorial we will be installing two offline speech to text engines (pocketsphinx and deepspeech) and one offline text to speech engine with a variety of voices (flite). This will allow your virtual assistant to function without an internet connection and without inadvertently sharing your conversations with any 3rd parties.

What I need you to bring is a virtual machine running Debian Stretch from the 1st DVD ([debian-9.4.0-amd64-DVD-1.iso]("https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/debian-9.4.0-amd64-DVD-1.iso")) which you can download from https://cdimage.debian.org/debian-cd/current/amd64/iso-dvd/ (or get the 32 bit version from https://cdimage.debian.org/debian-cd/current/i386/iso-dvd/debian-9.4.0-i386-DVD-1.iso if that's how you roll). It also has to have access to speakers and a microphone to work.

I have prepared a video at https://www.youtube.com/watch?v=15V76DZKXPs explaining exactly what to do.

Use whatever virtual machine container you are comfortable with QEMU, VirtualBox, VMWare, Hyper-V, etc. Basically, create a virtual machine with 1GiB RAM, a 10GiB hard drive, and as many processors as you can spare. Select only the SSH Server and Standard

The only requirement is that you make sure the guest operating system has access to the host machine’s microphone and speakers.
Basic setup parameters include 1024 MB RAM, 10GiB hard drive, 2 processors. The only options you need to select under “Software selection” are “standard system utilities” and “SSH Server” (which will allow you to communicate more directly with your virtual machine).

In the process you will be asked to assign a password to the root user, and create a regular, non-root, user and password. I am using “jasper” as my regular user, you can use whatever you want, but remember to change “jasper” to the name of your user below.
Start by giving your regular user (jasper) sudo privileges:


Re-mount your DVD iso (rebooting after install will usually unmount it) and log in as root

Add the cdrom as a repository (I'm trying to avoid any issues with flaky wi-fi)
<pre>
# apt-cdrom add
Install sudo and add your user to the sudo group
# apt install sudo
# usermod -aG sudo jasper
# exit
</pre>

Log in as your regular user and install alsa-utils
<pre>
$ sudo apt install alsa-utils
</pre>

record and play yourself speaking
<pre>
$ arecord -d 3 test.wav
$ aplay test.wav
</pre>

If you hear your voice, then congratulations, you are set up.

Please check back, I will also be posting a tar file containing files needed for the workshop (which will also be available on usb zip drive at the tutorial).

Thanks,
Aaron
