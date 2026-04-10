#!/usr/bin/env python3

import argparse
import csv
import sys
from datetime import date, timedelta
from enum import Enum
from pathlib import Path

FILE_PATH = Path.home() / "timeTracker" / "log.csv"
HEADER = ["Date", "Time", "Notes"]

PROG_NAME = "timeTracker"

CMD_READ  = "read"
CMD_WRITE = "write"
CMD_GRAPH = "graph"

OPT_VALUE  = "value"
OPT_OFFSET = "offset"
OPT_DATE   = "date"
OPT_NOTE   = "note"
OPT_MODE   = "mode"
OPT_SPAN   = "span"


class GraphMode(Enum):
    TOTAL  = "net"   # running cumulative total at end of each day
    LOGGED = "log"  # time logged on each individual day


DEFAULT_GRAPH_MODE = GraphMode.TOTAL
DEFAULT_GRAPH_SPAN = 30   # days back from today; graph shows span+1 columns


def ensure_file():
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not FILE_PATH.exists():
        with FILE_PATH.open("w", newline="") as f:
            csv.writer(f).writerow(HEADER)


def build_parser():
    parser = argparse.ArgumentParser(prog=PROG_NAME)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser(CMD_READ, help="Print the total sum of logged time")

    write_cmd = subparsers.add_parser(CMD_WRITE, help="Log a time entry")
    write_cmd.add_argument(OPT_VALUE, type=float, help="Time value to log (can be negative)")
    write_cmd.add_argument(f"--{OPT_OFFSET}", type=int, default=None, metavar="DAYS",
                           help="Day offset from today (e.g. -1 for yesterday)")
    write_cmd.add_argument(f"--{OPT_DATE}", default=None, metavar="YYYY-MM-DD",
                           help="Explicit date (overrides --offset)")
    write_cmd.add_argument(f"--{OPT_NOTE}", default="", help="Optional note for this entry")

    graph_cmd = subparsers.add_parser(CMD_GRAPH, help="Display a bar graph of logged time")
    graph_cmd.add_argument(
        f"--{OPT_MODE}",
        choices=[m.value for m in GraphMode],
        default=DEFAULT_GRAPH_MODE.value,
        help=f"Graph mode (default: {DEFAULT_GRAPH_MODE.value})",
    )
    graph_cmd.add_argument(
        f"--{OPT_SPAN}",
        type=int,
        default=DEFAULT_GRAPH_SPAN,
        metavar="DAYS",
        help=f"Days back to display (default: {DEFAULT_GRAPH_SPAN})",
    )

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


def read_all_entries():
    """Return all log entries as a list of (date, float) tuples."""
    if not FILE_PATH.exists():
        return []
    entries = []
    with FILE_PATH.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                entries.append((
                    date.fromisoformat(row["Date"].strip()),
                    float(row["Time"].strip()),
                ))
            except (ValueError, KeyError):
                pass
    return entries


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


def compute_daily_values(entries, days, mode):
    """Return a list of float values aligned to days, according to mode."""
    daily_sums = {}
    for entry_date, value in entries:
        daily_sums[entry_date] = daily_sums.get(entry_date, 0.0) + value

    if mode == GraphMode.LOGGED:
        return [daily_sums.get(d, 0.0) for d in days]

    # TOTAL: running cumulative sum at end of each day
    running = sum(v for d, v in daily_sums.items() if d < days[0])
    values = []
    for d in days:
        running += daily_sums.get(d, 0.0)
        values.append(running)
    return values


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


def cmd_graph(args):
    from graph import render_graph

    mode = GraphMode(getattr(args, OPT_MODE))
    span = getattr(args, OPT_SPAN)

    today = date.today()
    # span=30 → columns for days -30 … 0 inclusive (31 columns, so -30 tick appears)
    days   = [today - timedelta(days=(span - i)) for i in range(span + 1)]
    values = compute_daily_values(read_all_entries(), days, mode)
    render_graph(days, values, mode.value.upper(), span)


def main():
    args = build_parser().parse_args()

    if args.command == CMD_READ:
        cmd_read(args)
    elif args.command == CMD_WRITE:
        cmd_write(args)
    elif args.command == CMD_GRAPH:
        cmd_graph(args)


if __name__ == "__main__":
    main()
