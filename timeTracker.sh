#!/usr/bin/env bash

FILE_NAME="log.csv"
FILE_PATH="$HOME/timeTracker"
FILE="${FILE_PATH}/${FILE_NAME}"

usage() {
  echo "Usage:"
  echo "  timeTracker.sh read                                                              # print sum"
  echo "  timeTracker.sh write <float> [--offset=<days>] [--date=YYYY-MM-DD] [--note=<string>]"
  exit 1
}

cmd_read() {
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
}

cmd_write() {
  local time_val="$1"
  shift

  if [[ -z "$time_val" ]]; then
    echo "Error: write requires a float value" >&2
    usage
  fi

  if ! echo "$time_val" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
    echo "Error: '$time_val' is not a valid float" >&2
    usage
  fi

  local offset="" date_val="" note=""

  for arg in "$@"; do
    case "$arg" in
      --offset=*)  offset="${arg#--offset=}" ;;
      --date=*)    date_val="${arg#--date=}" ;;
      --note=*)    note="${arg#--note=}" ;;
      *) echo "Error: unknown argument '$arg'" >&2; usage ;;
    esac
  done

  local final_date
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

  local safe_note="${note//\"/\"\"}"
  if [[ "$safe_note" == *","* || "$safe_note" == *'"'* ]]; then
    safe_note="\"${safe_note}\""
  fi

  mkdir -p "$FILE_PATH"
  if [[ ! -f "$FILE" ]]; then
    echo "Date,Time,Notes" > "$FILE"
  fi

  echo "${final_date},${time_val},${safe_note}" >> "$FILE"
  echo "Written: ${final_date}, ${time_val}${note:+, \"$note\"}"
}

# Dispatch
case "${1:-}" in
  read)  shift; cmd_read "$@" ;;
  write) shift; cmd_write "$@" ;;
  *)     usage ;;
esac
