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
CMD_LOG   = "log"
CMD_EDIT  = "edit"

OPT_VALUE  = "value"
OPT_OFFSET = "offset"
OPT_DATE   = "date"
OPT_NOTE   = "note"
OPT_MODE   = "mode"
OPT_SPAN   = "span"
OPT_COUNT  = "count"


class GraphMode(Enum):
    TOTAL  = "net"   # running cumulative total at end of each day
    LOGGED = "log"  # time logged on each individual day


DEFAULT_GRAPH_MODE = GraphMode.TOTAL
DEFAULT_GRAPH_SPAN = 30   # days back from today; graph shows span+1 columns
DEFAULT_LOG_COUNT  = 10


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

    edit_cmd = subparsers.add_parser(CMD_EDIT, help="Edit the last log entry")
    edit_cmd.add_argument(OPT_VALUE, type=float, help="New time value")
    edit_cmd.add_argument(OPT_NOTE, nargs="*", help="New note (optional; words need not be quoted)")

    log_cmd = subparsers.add_parser(CMD_LOG, help="Display recent entries as a table")
    log_cmd.add_argument(
        OPT_COUNT, type=int, nargs="?", default=DEFAULT_LOG_COUNT, metavar="N",
        help=f"Number of entries to show (default: {DEFAULT_LOG_COUNT})",
    )

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


def read_all_entries_full():
    """Return all log entries as a list of (date, float, str) tuples including notes."""
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
                    row.get("Notes", "").strip(),
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


def edit_last_entry(value, note):
    if not FILE_PATH.exists():
        sys.exit("Error: no log file found.")
    with FILE_PATH.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit("Error: log is empty.")
    rows[-1]["Time"]  = value
    rows[-1]["Notes"] = note
    with FILE_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)


def cmd_edit(args):
    value = getattr(args, OPT_VALUE)
    note  = " ".join(getattr(args, OPT_NOTE))
    edit_last_entry(value, note)
    note_part = f', "{note}"' if note else ""
    print(f"Updated last entry: {value}{note_part}")


def cmd_log(args):
    count   = getattr(args, OPT_COUNT)
    entries = read_all_entries_full()

    if not entries:
        print("No entries found.")
        return

    # Build rows with running totals
    running = 0.0
    rows = []
    for entry_date, value, note in entries:
        running += value
        rows.append((entry_date, value, running, note))

    rows = rows[-count:]

    def fmt(v):
        return f"{v:.2f}".rstrip("0").rstrip(".")

    RED   = "\033[1;31m"
    GREEN = "\033[1;32m"
    DIM   = "\033[2m"
    RESET = "\033[0m"

    date_w    = 10
    logged_w  = max(len("Logged"), max(len(fmt(r[1])) for r in rows))
    total_w   = max(len("Total"),  max(len(fmt(r[2])) for r in rows))

    header = f"{'Date':<{date_w}}  {'Logged':>{logged_w}}  {'Total':>{total_w}}  Note"
    sep    = f"{'─' * date_w}  {'─' * logged_w}  {'─' * total_w}  {'─' * 4}"
    print(header)
    print(sep)

    for entry_date, value, total, note in rows:
        logged_s = fmt(value)
        total_s  = fmt(total)
        logged_col = f"{RED if value < 0 else GREEN}{logged_s:>{logged_w}}{RESET}"
        total_col  = f"{RED if total  < 0 else GREEN}{total_s:>{total_w}}{RESET}"
        note_col   = f"{DIM}{note}{RESET}" if note else ""
        print(f"{entry_date.isoformat():<{date_w}}  {logged_col}  {total_col}  {note_col}")


def main():
    args = build_parser().parse_args()

    if args.command == CMD_READ:
        cmd_read(args)
    elif args.command == CMD_WRITE:
        cmd_write(args)
    elif args.command == CMD_EDIT:
        cmd_edit(args)
    elif args.command == CMD_LOG:
        cmd_log(args)
    elif args.command == CMD_GRAPH:
        cmd_graph(args)


if __name__ == "__main__":
    main()
