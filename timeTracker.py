#!/usr/bin/env python3

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

FILE_PATH = Path.home() / "timeTracker" / "log.csv"
HEADER = ["Date", "Time", "Notes"]

PROG_NAME = "timeTracker"

CMD_READ = "read"
CMD_WRITE = "write"

OPT_VALUE = "value"
OPT_OFFSET = "offset"
OPT_DATE = "date"
OPT_NOTE = "note"


def ensure_file():
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FILE_PATH.exists():
        with FILE_PATH.open("w", newline="") as f:
            csv.writer(f).writerow(HEADER)


def build_parser():
    parser = argparse.ArgumentParser(prog=PROG_NAME)
    subparsers = parser.add_subparsers(dest=DEST_COMMAND, required=True)

    subparsers.add_parser(CMD_READ, help="Print the total sum of logged time")

    write_cmd = subparsers.add_parser(CMD_WRITE, help="Log a time entry")
    write_cmd.add_argument(OPT_VALUE, type=float, help="Time value to log (can be negative)")
    write_cmd.add_argument(f"--{OPT_OFFSET}", type=int, default=None, metavar="DAYS",
                           help="Day offset from today (e.g. -1 for yesterday)")
    write_cmd.add_argument(f"--{OPT_DATE}", default=None, metavar="YYYY-MM-DD",
                           help="Explicit date (overrides --offset)")
    write_cmd.add_argument(f"--{OPT_NOTE}", default="", help="Optional note for this entry")

    return parser


def sum_logged_time():
    if not FILE_PATH.exists():
        return 0.0

    total = 0.0
    with FILE_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                total += float(row["Time"].strip())
            except (ValueError, KeyError):
                pass
    return total


def resolve_date(date_str, offset):
    if date_str:
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            sys.exit(f"Error: invalid --{OPT_DATE} value '{date_str}'")
    if offset is not None:
        return date.today() + timedelta(days=offset)
    return date.today()


def append_entry(entry_date, value, note):
    ensure_file()
    with FILE_PATH.open("a", newline="") as f:
        csv.writer(f).writerow([entry_date.isoformat(), value, note or ""])


def cmd_read(_args):
    total = sum_logged_time()
    formatted = f"{total:.2f}".rstrip("0").rstrip(".")
    color = "\033[1;31m" if total < 0 else "\033[1;32m"
    print(f"{color}{formatted}\033[0m")


def cmd_write(args):
    resolved = resolve_date(getattr(args, OPT_DATE), getattr(args, OPT_OFFSET))
    note = getattr(args, OPT_NOTE)
    append_entry(resolved, getattr(args, OPT_VALUE), note)
    note_part = f', "{note}"' if note else ""
    print(f"Written: {resolved.isoformat()}, {getattr(args, OPT_VALUE)}{note_part}")


def main():
    args = build_parser().parse_args()

    if getattr(args, DEST_COMMAND) == CMD_READ:
        cmd_read(args)
    elif getattr(args, DEST_COMMAND) == CMD_WRITE:
        cmd_write(args)


if __name__ == "__main__":
    main()
