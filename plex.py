#!/usr/bin/python3

import os
import fnmatch
import subprocess
from time import sleep
import traceback

# Allows the script to be run as a cron job without failing with path errors
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

PLEX = "/PATH/TO/PLEX/FOLDER/"
VIDEOS = "/PATH/TO/OUTPUT/FOLDER/"
COMSKIP = "/usr/local/bin/comskip"
LOGFILE = "/PATH/TO/vrdwatch.log"
PROCESSING_FILES = "processing.txt"
PROCESSED_FILES = "processed_plex.txt"
IGNORED_FILES = "ignore_list.txt"


class TerminalColours:
    """ANSI Escape Codes to add text colours in the terminal to make it easier to see what's going on"""
    GREEN = "\u001b[32m"
    BLUE = "\x1B[34m"
    MAGENTA = "\x1B[35m"
    YELLOW = "\x1B[33m"
    RED = "\x1B[31m"
    RESET = "\u001b[0m"


def text_file_check():
    """Check to see if the processed and ignored text files exist; create them if they don't"""
    text_files = [PROCESSING_FILES, PROCESSED_FILES, IGNORED_FILES]
    for text_file in text_files:
        if not os.path.exists(text_file):
            with open(text_file, 'w'):
                pass


def ignored_shows(filename):
    with open(IGNORED_FILES, "r") as il:
        ignored = il.readlines()
        for line in ignored:
            ignored_file = line.strip("\n")
            if ignored_file == "":
                continue  # Skip empty lines
            if ignored_file in str(filename):
                return True
        return False


def check_processing(filename):
    """Checks to see if we are currently processed the recording and have added it to processing.txt"""
    with open(PROCESSING_FILES, "r") as pf:
        file_check = pf.readlines()
        for entry in file_check:
            if str(filename) in entry:
                return True
        return False


def check_processed(filename):
    """Checks to see if we have already processed the recording and added it to processed.txt"""
    with open(PROCESSED_FILES, "r") as pf:
        file_check = pf.readlines()
        for entry in file_check:
            if str(filename) in entry:
                return True
        return False


def on_disk(filename):
    """Checks the files on disk"""
    for root, dirs, files in os.walk(PLEX):
        if filename in files:
            return True
    return False


def file_size_check(video):
    """Returns the file size for each video"""
    return os.stat(video).st_size


def is_recording(video):
    """Checks to see if the recording is still in progress; ignores it if it is"""
    print(f"{TerminalColours.GREEN}Checking {video}'s file size to see if recording is"
          f" still active.{TerminalColours.RESET}")
    first_check = file_size_check(video)
    print(f"{TerminalColours.MAGENTA}First Check - current file size is {first_check}")
    sleep(5)
    second_check = file_size_check(video)
    print(f"Second Check - current file size is {second_check}{TerminalColours.RESET}")
    if second_check > first_check:
        print(f"{TerminalColours.YELLOW}{video} is still recording or QSF running; "
              f"skipping for now{TerminalColours.RESET}")
        return True
    else:
        return False


def delete_extra_files(file, videos_path):
    """Deletes all the extra files comskip creates when scanning for adverts"""
    try:
        filename = os.path.splitext(file)[0]
        os.remove(os.path.join(videos_path, f"{filename}.txt"))
        os.remove(os.path.join(videos_path, f"{filename}.edl"))
        os.remove(os.path.join(videos_path, f"{filename}.log"))
    except FileNotFoundError:
        with open(LOGFILE, "a") as error_log:
            traceback.print_exc(file=error_log)


def processed_exist_check():
    """Check to see if the processed files still exist on the disk; delete them from the list if not"""
    with open(PROCESSED_FILES, "r") as pf:
        lines = pf.readlines()
        with open(PROCESSED_FILES, "w") as removing:
            for line in lines:
                proc_line = line.strip("\n")
                # Call the on_disk method; checks if a file exists and matches an entry in processed.txt
                if on_disk(proc_line):
                    removing.write(line)


def processing_complete(filename):
    """When the file has completed processing remove it from processing.txt"""
    with open(PROCESSING_FILES, "r") as pf:
        lines = pf.readlines()
        with open(PROCESSING_FILES, "w") as removing:
            for line in lines:
                proc_line = line.strip("\n")
                if proc_line != filename:
                    removing.write(line)


text_file_check()
processed_exist_check()

print(f"{TerminalColours.GREEN}Checking Plex folder for new files.\n{TerminalColours.RESET}")
for root, dirs, files in os.walk(PLEX):
    for file in files:
        if fnmatch.fnmatch(file, "*.ts"):
            full_path = os.path.join(root, file)
            if ignored_shows(file):
                print(f"{TerminalColours.RED}{file} is in the ignore list.  Not processing.\n{TerminalColours.RESET}")
                continue
            if check_processed(file):
                continue
            if check_processing(file):
                continue
            if is_recording(full_path):
                continue
            else:
                with open(PROCESSING_FILES, "a") as processing:
                    processing.write(f"{file}\n")
                print(f"{TerminalColours.BLUE}Processing {file}{TerminalColours.RESET}")
                result = subprocess.run([COMSKIP, "--ts", "--quiet", "--vdpau", "--ini=comskip.ini",
                                         f"--output={VIDEOS}", full_path])
                with open(PROCESSED_FILES, "a") as completed:
                    completed.write(f"{file}\n")
                    processing_complete(file)
                    print(f"{TerminalColours.GREEN}Deleting redundant comskip files.\n{TerminalColours.RESET}")
                    delete_extra_files(file, VIDEOS)
