#!/usr/bin/env python3

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

FILE_PATH = Path.home() / "timeTracker" / "log.csv"
HEADER = ["Date", "Time", "Notes"]


def ensure_file():
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FILE_PATH.exists():
        with FILE_PATH.open("w", newline="") as f:
            csv.writer(f).writerow(HEADER)


def build_parser():
    parser = argparse.ArgumentParser(prog="timeTracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("read", help="Print the total sum of logged time")

    write_cmd = subparsers.add_parser("write", help="Log a time entry")
    write_cmd.add_argument("value", type=float, help="Time value to log (can be negative)")
    write_cmd.add_argument("--offset", type=int, default=None, metavar="DAYS",
                           help="Day offset from today (e.g. -1 for yesterday)")
    write_cmd.add_argument("--date", default=None, metavar="YYYY-MM-DD",
                           help="Explicit date (overrides --offset)")
    write_cmd.add_argument("--note", default="", help="Optional note for this entry")

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
            sys.exit(f"Error: invalid --date value '{date_str}'")
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
    resolved = resolve_date(args.date, args.offset)
    append_entry(resolved, args.value, args.note)
    note_part = f', "{args.note}"' if args.note else ""
    print(f"Written: {resolved.isoformat()}, {args.value}{note_part}")


def main():
    args = build_parser().parse_args()

    if args.command == "read":
        cmd_read(args)
    elif args.command == "write":
        cmd_write(args)


if __name__ == "__main__":
    main()
