#!/usr/bin/env python3
"""
vrdwatch_unified_lock_fixed.py
------------------------------
Unified advert-scan script for Tvheadend + Plex/Jellyfin.

Note:
- .VPrj creation depends on your comskip.ini settings (VideoReDo output enabled).
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import subprocess
import traceback
from pathlib import Path
from time import sleep
from typing import Iterable, List

DEFAULT_INPUT_ROOTS = [
    "/RECORDINGS/LOCATION/",
    "/ANOTHER/RECORDINGS/LOCATION/",
]

DEFAULT_OUTPUT_DIR = "/OUTPUT/PATH/HERE/"
DEFAULT_COMSKIP = "/PATH/TO/COMSKIP/EXECUTABLE"
DEFAULT_LOGFILE = "/PATH/TO/LOGFILE/vrdwatch.log"

DEFAULT_COMSKIP_ARGS = [
    "--ts",
    "--quiet",
    "--vdpau",
    "--ini=comskip.ini",
]

LOCK_FILE = "vrdwatch.lock"
PROCESSED_FILE = "processed.txt"
IGNORE_FILE = "ignore_list.txt"

DEFAULT_PATTERN = "*.ts"
DEFAULT_SIZE_CHECK_SECONDS = 5


def pid_is_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def acquire_lock(script_dir: Path) -> bool:
    lock = script_dir / LOCK_FILE
    if lock.exists():
        try:
            pid = int(lock.read_text().strip())
            if pid_is_alive(pid):
                print(f"Another instance is running (PID {pid}); exiting.")
                return False
        except Exception:
            pass
    lock.write_text(str(os.getpid()))
    return True


def release_lock(script_dir: Path) -> None:
    try:
        (script_dir / LOCK_FILE).unlink()
    except FileNotFoundError:
        pass


def read_list(path: Path) -> List[str]:
    if not path.exists():
        return []
    out: List[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for raw in f:
            s = raw.strip()
            if not s or s.startswith("#"):
                continue
            out.append(s)
    return out


def append_line(path: Path, line: str) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{line}\n")


def cleanup_processed(path: Path) -> None:
    if not path.exists():
        return

    original = read_list(path)
    keep = [p for p in original if Path(p).exists()]

    if keep == original:
        return  # nothing changed → do not rewrite

    path.write_text("\n".join(keep) + ("\n" if keep else ""))


def is_ignored(video: Path, patterns: List[str]) -> bool:
    s_full = str(video)
    s_name = video.name
    for pat in patterns:
        if pat in s_full or pat in s_name:
            return True
        if fnmatch.fnmatch(s_name, pat) or fnmatch.fnmatch(s_full, pat):
            return True
    return False


def is_still_writing(video: Path, seconds: int) -> bool:
    first = video.stat().st_size
    sleep(seconds)
    second = video.stat().st_size
    return second > first


def iter_videos(roots: Iterable[Path], pattern: str) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob(pattern):
            if p.is_file():
                yield p


def run_comskip(comskip: Path, base_args: List[str], output_dir: Path, video: Path) -> subprocess.CompletedProcess:
    cmd = [str(comskip), *base_args, f"--output={str(output_dir)}", str(video)]
    return subprocess.run(cmd, capture_output=True, text=True)


def delete_comskip_extras(video: Path, output_dir: Path, logfile: Path) -> None:
    stem = video.stem
    for ext in (".txt", ".edl", ".log"):
        p = output_dir / f"{stem}{ext}"
        try:
            p.unlink()
        except FileNotFoundError:
            pass
        except Exception:
            logfile.parent.mkdir(parents=True, exist_ok=True)
            with logfile.open("a", encoding="utf-8") as log:
                log.write(f"\n--- Failed deleting {p}\n")
                traceback.print_exc(file=log)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan recordings for adverts using comskip (Tvheadend + Plex/Jellyfin).")

    parser.add_argument("--input-root", action="append", dest="input_roots",
                        help="Root folder to scan (can be provided multiple times).")

    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Where comskip writes outputs (e.g. .VPrj).")

    parser.add_argument("--comskip", default=DEFAULT_COMSKIP,
                        help="Path to comskip executable.")

    parser.add_argument("--pattern", default=DEFAULT_PATTERN,
                        help="Filename glob pattern (default: *.ts).")

    parser.add_argument("--size-check-seconds", type=int, default=DEFAULT_SIZE_CHECK_SECONDS,
                        help="Seconds between size checks to detect active recordings.")

    parser.add_argument("--no-delete-extras", action="store_true",
                        help="Do not delete comskip .txt/.edl/.log sidecars in output dir.")

    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)

    if not acquire_lock(script_dir):
        return 0

    try:
        roots = [Path(p) for p in (args.input_roots if args.input_roots else DEFAULT_INPUT_ROOTS)]
        output_dir = Path(args.output_dir)
        comskip = Path(args.comskip)
        logfile = Path(DEFAULT_LOGFILE)

        output_dir.mkdir(parents=True, exist_ok=True)

        processed_path = script_dir / PROCESSED_FILE
        ignore_path = script_dir / IGNORE_FILE
        if not processed_path.exists():
            processed_path.touch()
        if not ignore_path.exists():
            ignore_path.touch()


        cleanup_processed(processed_path)

        processed = set(read_list(processed_path))
        ignored = read_list(ignore_path)

        for video in iter_videos(roots, args.pattern):
            v = str(video)

            if v in processed:
                continue
            if is_ignored(video, ignored):
                continue

            try:
                if is_still_writing(video, args.size_check_seconds):
                    continue
            except FileNotFoundError:
                continue

            print(f"Processing {video}")
            result = run_comskip(comskip, DEFAULT_COMSKIP_ARGS, output_dir, video)

            # comskip returns non-zero when no commercials are found (not an error)
            if result.returncode != 0 and "Commercials were not found" not in result.stdout:
                logfile.parent.mkdir(parents=True, exist_ok=True)
                with logfile.open("a", encoding="utf-8") as log:
                    log.write(f"\n--- comskip FAILED: {video}\n")
                    log.write("CMD: " + " ".join([str(comskip), *DEFAULT_COMSKIP_ARGS, f"--output={output_dir}", str(video)]) + "\n")
                    log.write(result.stdout or "")
                    log.write(result.stderr or "")
                continue

            append_line(processed_path, v)
            processed.add(v)

            if not args.no_delete_extras:
                delete_comskip_extras(video, output_dir, logfile)

    finally:
        release_lock(script_dir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
