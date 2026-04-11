# timeTracker

A simple CLI tool for tracking banked time.

## Recommended Setup

**1. Make the script executable:**

```bash
chmod +x {path-to-timeTracker}/timeTracker/timeTracker.py
```

**2. Add to PATH** so you can run `timeTracker.py` from any directory.

Add this line to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="{path-to-timeTracker}/timeTracker:$PATH"
```

Then reload your shell:

```bash
source ~/.bashrc   # or source ~/.zshrc
```

**3. Optional — create a shorter alias:**

Add to the same shell config file to avoid typing the `.py` extension:

```bash
alias tt="timeTracker.py"
```

After setup you can run from anywhere:

```bash
timeTracker.py write 1.5
timeTracker.py graph
```

Or with the alias:

```bash
timetracker write 1.5
timetracker graph
```

## Usage

```bash
timeTracker.py <command> [options]
```

### Commands

| Command | Description |
|---|---|
| `read` | Print the total sum of all logged time |
| `write <value>` | Log a time value (positive or negative) |
| `edit <value> [note]` | Overwrite the last log entry |
| `log [N]` | Show the last N entries as a table (default: 10) |
| `graph` | Display a bar graph of logged time |

### `write` options

| Flag | Description |
|---|---|
| `--note="..."` | Attach a note to the entry |
| `--offset=<n>` | Days offset from today (e.g. `-1` for yesterday) |
| `--date=YYYY-MM-DD` | Log to a specific date (overrides `--offset`) |

### `graph` options

| Flag | Description |
|---|---|
| `--mode=net\|log` | `net` = running cumulative total (default); `log` = daily logged amount |
| `--span=<n>` | Days back to display (default: `30`) |

## Examples

```bash
python3 timeTracker.py write 1.5                          # log 1.5 today
python3 timeTracker.py write -0.5 --note="correction"    # subtract with a note
python3 timeTracker.py write 2 --offset=-1               # log 2 to yesterday
python3 timeTracker.py write 3 --date=2026-03-28         # log to a specific date
python3 timeTracker.py edit 1.5                          # fix last entry value
python3 timeTracker.py edit 1.5 forgot to mention this   # fix value and note
python3 timeTracker.py read                              # print total
python3 timeTracker.py log                               # show last 10 entries
python3 timeTracker.py log 25                            # show last 25 entries
python3 timeTracker.py graph                             # net total graph, last 30 days
python3 timeTracker.py graph --mode=log --span=14        # daily graph, last 14 days
```

## Data

Entries are stored in `~/timeTracker/log.csv` (created automatically):

```
Date,Time,Notes
2026-03-31,1.5,
2026-03-31,-0.5,correction
```
