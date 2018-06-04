jasper-client
=============

Client code for the Jasper voice computing platform. Jasper is an open source platform for developing always-on, voice-controlled applications. What makes Jasper different from other voice activated assistants is that Jasper can pretty much run on your local hardware, without sending recordings of your voice off to the cloud for transcribing. Not only does this circumvent many privacy issues, but right now it means that it can do things the corporate systems can't. It is trivial, for example, to change Jasper's wake word to any name you want, or even a variety of names and nicknames.

The original development team for Jasper (who I have never met or worked with) did a great job of writing Jasper to be general purpose. It is easy to customize and write new libraries for speech to text recognition, text to speech, different audio subsystems, etc. This was the first thing that attracted me to this project, as my original goal was just to experiment with and understand better how to use different speech to text systems.

I believe my goals are different from those of the original development team. I believe that their intention was to write a voice assistant, that was configurable for lots of different applications, and they succeeded in that. My goal is to facilitate training these tools to your individual speaking voice and accent, and languages other than english, and experiment with how an audio desktop would work. My goal is to eventually make the internet and computing in general more accessible to people with mobility and/or vision issues by translating as much as possible to the speech/audible world.

I also intend to add the ability to train this system to recognize individual voices and respond uniquely to each user (allowing users to maintain own shopping lists, music collections, etc). I am also working on making interactions with Jasper more conversational.

Please be aware that if you enable recording of active listening, passive listening and/or noise, the computer will be creating audio files on your hard drive and maintaining a database of these samples with transcriptions. These audio recordings are not uploaded to the cloud or intended to be used by anyone but you, but you should limit the recording to times when everyone knows they are being recorded.

Step by step instructions for setting up and testing Pocketsphinx are listed in [PocketSphinx_setup.md](https://github.com/aaronchantrill/jasper-client/blob/master/PocketSphinx_setup.md). This version of Jasper has been tested with both the old 1.3.4 and the new 1.6.7 versions of OpenFST, and I imagine it would work with anything in between. I'll be trying to stay up to date with the latest versions of Phonetisaurus.

Step by step instructions for setting up this version of Jasper can found in [build_instructions.md](https://github.com/aaronchantrill/jasper-client/blob/master/build_instructions.md). These instructions cover setting up Jasper to use PocketSphinx for passive listening (because it is fast and only accurate when using a small dictionary) and DeepSpeech for active listening (because it is slow and still has accuracy issues, but a huge dictionary), festival for text to speech processing, and pyaudio for the audio subsystem. This is the setup I am currently using.

## Contributing

If you want to help, then that is fantastic. One of the great aspects of a project like this is that it incorporates a lot of different disciplines. Here's a list of projects I'd love help with:

1. Voice training database - I am currently working on creating a website which will allow me to listen to recordings and manually select the identity of the speaker and verify or correct the transcription. This is part one of my plan to improve usability by allowing users to train Jasper to particular voices and different languages and accents.
2. Better voice - Jasper can use several different text to speech libraries to talk. Personally, I tend to use Festival with Arctic voices because they are the right combination of ease of use and quality. If I could use higher quality voices, I would. Also, festival allows you to specify the speed, inflection, etc. of voices, which can be used to make Jasper sing, and could be incorporated into Jasper's personality. Personally, I would love to give Jasper Terry Gross's voice.
3. Visual feedback - It often takes time for Jasper to respond. During this time, it can be hard to tell if Jasper has heard you or not. Other projects have used light patterns or animated faces to let you know if the computer is waiting for a wake word, is preparing to respond, or has crashed. While I want to make sure the system is fully functional without any visual feedback, I recognize that some visual feedback can be helpful.
4. Better intention parser - Jasper's modules are currently activated by speaking particular phrases. This needs to be improved so that the intention remains clear when words are inserted or dropped or rearranged in the command.
5. Audible desktop - Audible computing is currently something like a command line. That is part of the reason why I was interested in implementing text adventures as a first project. It occurs to me that the rich design of the unix command line can probably be used to design a audible command line in which commands can be strung together in ways that hopefully feel somewhat natural, or at least become logical after a little practice.

If you'd like to contribute to Jasper, please read through the **[Contributing Guide](CONTRIBUTING.md)**, which outlines the philosophies to preserve, tests to run, and more. We highly recommend reading through this guide before writing any code.

Thank you!

## Support

If you run into an issue or require technical support, please first look through the closed and open **[GitHub Issues](https://github.com/aaronchantrill/jasper-client/issues)**, as you may find a solution there (or some useful advice, at least).

## Contact

Jasper's original core developers are [Shubhro Saha](http://www.shubhro.com), [Charles Marsh](http://www.crmarsh.com) and [Jan Holthuis](http://homepage.ruhr-uni-bochum.de/Jan.Holthuis/).  All of them can be reached by email at [saha@princeton.edu](mailto:saha@princeton.edu), [crmarsh@princeton.edu](mailto:crmarsh@princeton.edu) and [jan.holthuis@ruhr-uni-bochum.de](mailto:jan.holthuis@ruhr-uni-bochum.de) respectively. Their version of Jasper can be found at [https://github.com/jasperproject/jasper-client](https://github.com/jasperproject/jasper-client).

This version of Jasper is maintained by Aaron Chantrill who can be contacted at [aaron.chantrill@dottywood.org](mailto:aaron.chantrill@dottywood.org). I began this from commit 1b102b1a9ce806c99f01fccea3aaf675b136031b of the Jasper-dev branch. I do not know and have not worked with any of the original core developers, but greatly appreciate all the effort they obviously put into this system.

For a semi-complete list of code contributors, please see [AUTHORS.md](AUTHORS.md).

## License

*Original Copyright (c) 2014-2015, Charles Marsh, Shubhro Saha & Jan Holthuis. All rights reserved.*

*Modifications Copyright (c) 2017-2018, Aaron Chantrill*

Jasper is covered by the MIT license, a permissive free software license that lets you do anything you want with the source code, as long as you provide back attribution and ["don't hold \[us\] liable"](http://choosealicense.com). For the full license text see the [LICENSE.md](LICENSE.md) file.
