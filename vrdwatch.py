import os
import fnmatch
import subprocess
from time import sleep

RECORDINGS = "/PATH/TO/RECORDINGS/FOLDER"
VIDEOS = "/PATH/TO/HD/RECORDINGS"
COMSKIP = "comskip"
HD_PROGRAMS = " HD "
ARG1 = "--ts"
ARG2 = "--quiet"
ARG3 = "--vdpau"
ARG4 = "--ini=comskip.ini"
ARG5 = "--output=/comskip/output/folder"
PROCESSED_FILES = "processed.txt"


def check_processed():
    """Checks to see if we have already processed the recording and added it to processed.txt"""
    try:
        with open(PROCESSED_FILES, "r") as pf:
            file_check = pf.readlines()
    except FileNotFoundError:
        with open(PROCESSED_FILES, "w+") as pf:
            file_check = pf.readlines()
    else:
        for entry in file_check:
            if str(file) in entry:
                return True
        return False


def on_disk(filename):
    """Checks the files on disk"""
    for vid in os.listdir(RECORDINGS):
        if vid == filename:
            return True
    return False


def file_size_check(video):
    """Returns the file size for each video"""
    return os.stat(os.path.join(RECORDINGS, video)).st_size


def is_recording(video):
    """Checks to see if the recording is still in process; ignores it if it is"""
    print("Checking file size")
    first_check = file_size_check(video)
    print(first_check)
    sleep(5)
    print("Rechecking file size to ensure it's not still recording")
    second_check = file_size_check(video)
    print(second_check)
    if second_check > first_check:
        return True
    else:
        return False


def delete_extra_files():
    """Deletes all the extra files comskip creates when scanning for adverts"""
    filename = os.path.splitext(file)[0]
    os.remove(f"{VIDEOS}{filename}.txt")
    os.remove(f"{VIDEOS}{filename}.edl")
    os.remove(f"{VIDEOS}{filename}.log")


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


processed_exist_check()

for file in os.listdir(RECORDINGS):
    if fnmatch.fnmatch(file, "*.ts"):
        if check_processed():
            continue
        if HD_PROGRAMS in file:
            continue  # QSF the file in VideoReDo before checking for adverts.  The output will be in the VIDEOS folder
        if is_recording(file):
            continue
        else:
            print(f"Processing {file}")
            result = subprocess.run([COMSKIP, ARG1, ARG2, ARG3, ARG4, ARG5, f"{RECORDINGS}{file}"])
            with open(PROCESSED_FILES, "a") as completed:
                completed.write(f"{file}\n")
                delete_extra_files()

for file in os.listdir(VIDEOS):
    if HD_PROGRAMS in file:
        if fnmatch.fnmatch(file, "*.ts"):
            if check_processed():
                continue
            print(f"Processing {file}")
            result = subprocess.run([COMSKIP, ARG1, ARG2, ARG3, ARG4, ARG5, f"{VIDEOS}{file}"])
            with open(PROCESSED_FILES, "a") as completed:
                completed.write(f"{file}\n")
                delete_extra_files()
