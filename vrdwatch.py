import os
import fnmatch
import subprocess
from time import sleep
import traceback

# Allows the script to be run as a cron job without failing with path errors
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)

RECORDINGS = "/PATH/TO/RECORDINGS/FOLDER"
VIDEOS = "/PATH/TO/HD/RECORDINGS"
COMSKIP = "/PATH/TO/COMSKIP/EXECUTABLE"
LOGFILE = "/PATH/TO/LOG/FILE"
HD_PROGRAMS = " HD "
ARG1 = "--ts"
ARG2 = "--quiet"
ARG3 = "--vdpau"
ARG4 = "--ini=comskip.ini"
ARG5 = "--output=/comskip/output/folder"
PROCESSED_FILES = "processed.txt"
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
    text_files = [PROCESSED_FILES, IGNORED_FILES]
    for text_file in text_files:
        if os.path.exists(text_file):
            return True
        else:
            os.mknod(text_file)


def ignored_shows(filename):
    with open("ignore_list.txt", "r") as il:
        ignored = il.readlines()
        for line in ignored:
            ignored_file = line.strip("\n")
            if ignored_file in str(filename):
                return True
        return False


def check_processed():
    """Checks to see if we have already processed the recording and added it to processed.txt"""
    with open(PROCESSED_FILES, "r") as pf:
        file_check = pf.readlines()
        for entry in file_check:
            if str(file) in entry:
                return True
        return False


def on_disk(filename):
    """Checks the files on disk"""
    if HIGH_DEF in filename:
        for vid in os.listdir(VIDEOS):
            if vid == filename:
                return True
        return False
    else:
        for vid in os.listdir(RECORDINGS):
            if vid == filename:
                return True
        return False


def file_size_check(video):
    """Returns the file size for each video"""
    if HIGH_DEF in video:
        return os.stat(os.path.join(VIDEOS, video)).st_size
    else:
        return os.stat(os.path.join(RECORDINGS, video)).st_size


def is_recording(video):
    """Checks to see if the recording is still in process; ignores it if it is"""
    print(f"{TerminalColours.GREEN}Checking {video}'s file size to see if recording is still active.{TerminalColours.RESET}")
    first_check = file_size_check(video)
    print(f"{TerminalColours.MAGENTA}First Check - current file size is {first_check}")
    sleep(5)
    second_check = file_size_check(video)
    print(f"Second Check - current file size is {second_check}{TerminalColours.RESET}")
    if second_check > first_check:
        print(f"{TerminalColours.YELLOW}{video} is still recording or QSF running; skipping for now{TerminalColours.RESET}")
        return True
    else:
        return False


def delete_extra_files():
    """Deletes all the extra files comskip creates when scanning for adverts"""
    try:
        filename = os.path.splitext(file)[0]
        os.remove(f"{VIDEOS}{filename}.txt")
        os.remove(f"{VIDEOS}{filename}.edl")
        os.remove(f"{VIDEOS}{filename}.log")
    except FileNotFoundError:
        traceback_output = traceback.format_exc()
        with open(LOGFILE, "w") as error_log:
            print(traceback_output, file=error_log)


def processed_exist_check():
    """Check to see if the processed files still exist on the disk; delete them from the list if not"""
    with open(PROCESSED_FILES, "r") as pf:
        lines = pf.readlines()
        with open(PROCESSED_FILES, "w") as removing:
            for number, line in enumerate(lines):
                proc_line = line.strip("\n")
                # Call the on_disk method; checks if a file exists and matches an entry in processed.txt
                if on_disk(proc_line):
                    temp_num = number
                    if number in [temp_num]:
                        removing.write(line)


text_file_check()
processed_exist_check()

# SD Recordings
print(f"{TerminalColours.GREEN}Checking recordings folder for new files.\n{TerminalColours.RESET}")
for file in os.listdir(RECORDINGS):
    if fnmatch.fnmatch(file, "*.ts"):
        if check_processed():
            continue
        if ignored_shows(file):
            print(f"{TerminalColours.RED}{file} is in the ignore list.  Not processing.{TerminalColours.RESET}")
            continue
        if HIGH_DEF in file:
            print(f"{TerminalColours.YELLOW}{file} is a HD recording.  QSF required before processing.\n{TerminalColours.RESET}")
            continue
        if is_recording(file):
            continue
        else:
            print(f"{TerminalColours.BLUE}Processing {file}{TerminalColours.RESET}")
            result = subprocess.run([COMSKIP, ARG1, ARG2, ARG3, ARG4, ARG5, f"{RECORDINGS}{file}"])
            with open(PROCESSED_FILES, "a") as completed:
                completed.write(f"{file}\n")
                print(f"{TerminalColours.GREEN}Deleting redundant comskip files.\n{TerminalColours.RESET}")
                delete_extra_files()

# HD Recordings
print(f"{TerminalColours.GREEN}Checking for new HD recordings.\n{TerminalColours.RESET}")
for file in os.listdir(VIDEOS):
    if HIGH_DEF in file and fnmatch.fnmatch(file, "*.ts"):
        if check_processed():
            continue
        if is_recording(file):
            continue
        else:
            print(f"{TerminalColours.BLUE}Processing {file}{TerminalColours.RESET}")
            result = subprocess.run([COMSKIP, ARG1, ARG2, ARG3, ARG4, ARG5, f"{VIDEOS}{file}"])
            with open(PROCESSED_FILES, "a") as completed:
                completed.write(f"{file}\n")
                print(f"{TerminalColours.GREEN}Deleting redundant comskip files.\n{TerminalColours.RESET}")
                delete_extra_files()
