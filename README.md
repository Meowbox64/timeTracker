# timeTracker

Track time by logging float values to a CSV file.

## Setup

```bash
chmod +x timeTracker.sh
```

## Usage

**Read** — print the sum of all logged time:
```bash
./timeTracker.sh
```

**Write** — log a time value (positive or negative):
```bash
./timeTracker.sh <float>
```

### Options

| Flag | Description |
|---|---|
| `--note="..."` | Attach a note to the entry |
| `--offset=<n>` | Days offset from today (e.g. `-1` for yesterday) |
| `--date=YYYY-MM-DD` | Log to a specific date |

## Examples

```bash
./timeTracker.sh 1.5                          # log 1.5 today
./timeTracker.sh -0.5 --note="correction"     # subtract with a note
./timeTracker.sh 2 --offset=-1                # log 2 to yesterday
./timeTracker.sh 3 --date=2026-03-28          # log to a specific date
./timeTracker.sh                              # print total
```

## Configuration

By default the CSV is created in the same directory as the script. If you invoke `timeTracker.sh` from elsewhere in the system (e.g. via a shell alias or `$PATH`), make CSV_PATH an absolute path so the file is always written to the same place:

```bash
CSV_FILE="$HOME/timeTracker/timeTracker.csv"
```

If the directory doesn't exist yet, add this line directly below:

```bash
mkdir -p "$(dirname "$CSV_FILE")"
```

## Data

Entries are stored in `timeTracker.csv` (created automatically):

```
Date,Time,Notes
2026-03-31,1.5,
2026-03-31,-0.5,correction
```
