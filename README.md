# vrdwatch
Advert detector, written in Python and using comskip

This was written as a solution for those of us that use [VideoReDo](https://web.archive.org/web/20221224201756/https://www.videoredo.com/en/index.htm)* on Linux and can't use VRD's batch manager or the VideoReDo Autoprocessor application as they both rely on COM calls that WINE can't currently deal with.

**What vrdwatch should do**

- Check one or more recordings folders for video files (currently set to .ts files, but this can be changed by editing the 'DEFAULT_PATTERN' entry in the script)
- Scan recordings folders recursively, so both flat and nested directory layouts are supported
- Check to see if the files have already been processed
- Check to see if the recording is still active and ignore it if that's the case
- Use a lock file so the script can be safely run at frequent intervals (e.g. via cron) without starting multiple comskip processes
- Check to see if the recording in the processed.txt file (automatically created if it doesn't exist) still exists on the disk and remove it from the text file if it doesn't
- Optionally you can use the ignore_list.txt file (automatically created if it doesn't exist) to add anything you don't want to process
- Automatically clean up comskip sidecar files (.txt, .edl, .log) after processing

**Setup Notes**

You will need to install Comskip which can also be found on [GitHub](https://github.com/erikkaashoek/Comskip).

You will also need your comskip.ini file, which should be placed in the same folder as this script.

There are a few additional constants that need to have paths set to make this work:

- DEFAULT_INPUT_ROOTS # One or more paths to your video recordings (each path is scanned recursively)
- DEFAULT_COMSKIP # Path to the comskip executable. Typing 'whereis comskip' at the terminal on Linux should help if you're struggling to find it
- DEFAULT_OUTPUT_DIR # Directory where comskip should write its output files (including .VPrj)
- DEFAULT_LOGFILE # Path to the log file (only written when comskip genuinely fails)
- DEFAULT_COMSKIP_ARGS # Additional arguments passed to comskip

You can either run this script manually when you want to or create a cron job to run it at intervals.

The script now supports both flat and nested recording directory layouts in a single file, so the previous Plex-specific script is no longer required.

**Running the Script**

You can run the script manually:

```./vrdwatch.py```

or via cron.

**Cron example**

```*/5 * * * * /path/to/vrdwatch/vrdwatch.py```

\* *The VideoReDo website no longer exists after the sad passing of its owner, Dan Rosen.  It is still possible to activate VideoReDo (though not the pro version) due to the ongoing efforts of the product's other developer, known as Dan203 on the VRD forum and [Reddit](https://www.reddit.com/r/videoredo/).  See the r/videoredo Rules section for further information.*
