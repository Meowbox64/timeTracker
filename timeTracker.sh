#!/usr/bin/env bash

FILE_NAME="timeTracker.csv"
FILE_PATH="."
FILE="${FILE_PATH}/${FILE_NAME}"

usage() {
  echo "Usage:"
  echo "  timeTracker.sh                                      # read: print sum"
  echo "  timeTracker.sh <float> [note] [--offset=<days>] [--date=YYYY-MM-DD]"
  exit 1
}

# No args = read
if [[ $# -eq 0 ]]; then
  if [[ ! -f "$FILE" ]]; then
    echo "0"
    exit 0
  fi

  total=$(tail -n +2 "$FILE" | awk -F',' '
    {
      val = $2
      gsub(/[[:space:]]/, "", val)
      if (val ~ /^-?[0-9]+(\.[0-9]+)?$/) sum += val
    }
    END {
      result = sprintf("%.2f", sum)
      sub(/\.?0+$/, "", result)
      print result
    }
  ')

  if echo "$total" | grep -q '^-'; then
    color="\033[1;31m"  # bold red
  else
    color="\033[1;32m"  # bold green
  fi
  printf "${color}%s\033[0m\n" "$total"

  exit 0
fi

# First arg is the float value to write
time_val="$1"
shift

# Validate float (allow negative)
if ! echo "$time_val" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
  echo "Error: '$time_val' is not a valid float" >&2
  usage
fi

# Second arg is optional note (if it doesn't start with --)
note=""
if [[ -n "$1" && "$1" != --* ]]; then
  note="$1"
  shift
fi

offset=""
date_val=""

for arg in "$@"; do
  case "$arg" in
    --offset=*)  offset="${arg#--offset=}" ;;
    --date=*)    date_val="${arg#--date=}" ;;
    *) echo "Error: unknown argument '$arg'" >&2; usage ;;
  esac
done

# Resolve date
if [[ -n "$date_val" ]]; then
  if ! date -d "$date_val" &>/dev/null 2>&1 && ! date -j -f "%Y-%m-%d" "$date_val" +%Y-%m-%d &>/dev/null 2>&1; then
    echo "Error: invalid --date value '$date_val'" >&2
    exit 1
  fi
  final_date="$date_val"
elif [[ -n "$offset" ]]; then
  if ! echo "$offset" | grep -qE '^-?[0-9]+$'; then
    echo "Error: --offset must be an integer, got '$offset'" >&2
    exit 1
  fi
  if date --version &>/dev/null 2>&1; then
    final_date=$(date -d "${offset} days" +%Y-%m-%d)
  else
    final_date=$(date -v "${offset}d" +%Y-%m-%d)
  fi
else
  final_date=$(date +%Y-%m-%d)
fi

# Escape any commas or quotes in note
safe_note="${note//\"/\"\"}"
if [[ "$safe_note" == *","* || "$safe_note" == *'"'* ]]; then
  safe_note="\"${safe_note}\""
fi

# Create CSV with header if it doesn't exist
if [[ ! -f "$FILE" ]]; then
  echo "Date,Time,Notes" > "$FILE"
fi

echo "${final_date},${time_val},${safe_note}" >> "$FILE"
echo "Written: ${final_date}, ${time_val}${note:+, \"$note\"}"
