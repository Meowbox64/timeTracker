# timeTracker

Track time by logging float values to a CSV file.

## Usage

```bash
python3 timeTracker.py <command> [options]
```

### Commands

| Command | Description |
|---|---|
| `read` | Print the total sum of all logged time |
| `write <value>` | Log a time value (positive or negative) |
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
python3 timeTracker.py read                              # print total
python3 timeTracker.py graph                             # net total graph, last 30 days
python3 timeTracker.py graph --mode=log --span=14        # daily graph, last 14 days
```

## Graph

The graph renders a vertical bar chart in the terminal. Positive values (green) stack upward; negative values (red) stack downward.

Values are resolved to 0.25-hour precision (half of the 0.5-hour step size). Each row represents 0.5 hours:

- A full-height bar uses a solid block character (`█`)
- A partial bar (0.25 h into a 0.5 h row) uses a half-block character:
  - Positive: `▄` (lower half) — sits atop the full block below
  - Negative: `▀` (upper half) — hangs below the full block above

## Data

Entries are stored in `~/timeTracker/log.csv` (created automatically):

```
Date,Time,Notes
2026-03-31,1.5,
2026-03-31,-0.5,correction
```
