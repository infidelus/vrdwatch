# vrdwatch
Advert detector, written in Python and using comskip

This was written as a solution for those of us that use [VideoReDo](https://www.videoredo.com)* on Linux and can't use VRD's batch manager or the VideoReDo Autoprocessor application as they both rely on COM calls that WINE can't currently deal with.

**What vrdwatch should do**

* Check your recordings folder for video files (currently set to .ts files, but you can change that to whatever format you record in)
* Check to see if the files have already been processed
* Check to see if the recording is still active and ignore it if that's the case
* Check to see if the recording in the processed.txt file (automatically created if it doesn't exist) still exists on the disk and remove it from the text file if it doesn't
* Optionally you can use the 'ignore_list.txt' file (automatically created if it doesn't exist) to add anything you don't want to process

**Setup Notes**

You will need to install Comskip which can also be found on [GitHub](https://github.com/erikkaashoek/Comskip).

You will also need your comskip.ini file.  I put mine in the same folder where this script is to make life easier.

There are a few additional constants that need to have paths set to make this work:

* RECORDINGS  # The path to your video recordings
* COMSKIP  # Add the path to the comskip executable.  Typing 'whereis comskip' at the terminal should help if you're struggling to find it
* ARGx  # You can add any number of arguments for Comskip.  I had trouble passing all the arguments as one variable so I separated them out which seems to work.  Be sure to edit the 'result' variable if you add or remove any of the arguments

I have a couple of extra constants (VIDEOS / HD_PROGRAMS) that I use as I run QuickStream Fix on HD files before I start editing them.  If all your recordings are HD, lucky you; you won't need to use the final for loop and can take out of the 'if HD_PROGRAMS in file:' section.

You can either run this script manually when you want to or create a cron job to run it at intervals.

There is also now an additional script for use with Plex or similar media servers so the recordings don't all need to be in one specific folder.  See PLEX.md for further info.

\* *The VideoReDo website no longer exists after the sad passing of its owner, Dan Rosen.  It is still possible to activate VideoReDo (though not the pro version) due to the ongoing efforts of the product's other developer, known as Dan203 on the VRD forum and [Reddit](https://www.reddit.com/r/videoredo/).*
