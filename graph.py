"""Graph rendering for timeTracker."""

from typing import Sequence

GRAPH_STEP = 0.5

LABEL_WIDTH   = 4   # chars reserved for y-axis labels (e.g. " 4.0", "-3.5")
TICK_INTERVAL = 5   # days between x-axis tick marks

_GREEN_BG = "\033[102m"
_RED_BG   = "\033[101m"
_RESET    = "\033[0m"
_BOLD     = "\033[1m"
_BLOCK    = " "


def render_graph(days: Sequence, values: Sequence[float], mode_label: str, span: int) -> None:
    """Render a bar graph to stdout.

    days       -- ordered sequence of date objects (oldest first, newest last)
    values     -- one float per day; positive = green bar up, negative = red bar down
    mode_label -- graph mode string shown in the side panel title (e.g. "TOTAL")
    span       -- the --span option value, shown in the side panel
    """
    span    = len(days)
    snapped = [_snap(v) for v in values]

    max_abs   = max((abs(v) for v in snapped), default=0.0)
    max_abs   = max(GRAPH_STEP, max_abs)   # at least one row above and below zero
    num_rows  = round(2 * max_abs / GRAPH_STEP)
    lines     = []

    lines.append(_top_border(span))

    for i in range(num_rows):
        top_val    = max_abs - i * GRAPH_STEP
        bottom_val = top_val - GRAPH_STEP
        # Positive rows: label shows top edge; negative rows: label shows bottom edge.
        label_val  = top_val if bottom_val >= -1e-9 else bottom_val
        lines.append(_content_row(label_val, top_val, bottom_val, snapped))

    lines.append(_bottom_border(span))
    lines += _x_axis(span)

    side = _side_panel(mode_label, span)
    gap  = "  "
    out  = []
    for i, line in enumerate(lines):
        # Attach side text starting on the row after the top border (i=1)
        text_idx = i - 1
        suffix = (gap + side[text_idx]) if 0 <= text_idx < len(side) else ""
        out.append(line + suffix)

    print("\n".join(out))


# ── row builders ────────────────────────────────────────────────────────────

def _top_border(span: int) -> str:
    return " " * LABEL_WIDTH + "┌" + "─" * span + "┐"


def _bottom_border(span: int) -> str:
    return " " * LABEL_WIDTH + "└" + "─" * span + "┘"



def _content_row(
    label_val: float,
    top_val: float,
    bottom_val: float,
    values: Sequence[float],
) -> str:
    cells = "".join(_cell_char(v, top_val, bottom_val) for v in values)
    return _fmt_label(label_val) + "│" + cells + "│"


# ── cell rendering ───────────────────────────────────────────────────────────

def _snap(value: float) -> float:
    """Round value to the nearest GRAPH_STEP increment."""
    return round(value / GRAPH_STEP) * GRAPH_STEP


def _fmt_label(value: float) -> str:
    return f"{value:4.1f}"


def _cell_char(value: float, top_val: float, bottom_val: float) -> str:
    """Return a coloured block if value falls in [bottom_val, top_val], else a space."""
    if value == 0.0:
        return " "
    if value > 0 and 0 <= bottom_val < value:
        return f"{_GREEN_BG}{_BLOCK}{_RESET}"
    if value < 0 and value < top_val <= 0:
        return f"{_RED_BG}{_BLOCK}{_RESET}"
    return " "


# ── x-axis ───────────────────────────────────────────────────────────────────

def _x_axis(span: int) -> list:
    """Two-line x-axis: tick marks and day-offset labels.

    Offsets are relative to today (0 = today = rightmost column).
    Labels are left-aligned from the tick position.
    """
    tick_chars  = [" "] * span
    label_chars = [" "] * span

    for i in range(span):
        offset = i - (span - 1)          # 0 at rightmost, negative going left
        if offset % TICK_INTERVAL == 0:
            tick_chars[i] = "│"
            label = str(offset)
            for j, ch in enumerate(label):
                pos = i + j
                if pos < span:
                    label_chars[pos] = ch

    pad = " " * (LABEL_WIDTH + 1)        # align with inner graph content
    return [
        pad + "".join(tick_chars),
        pad + "".join(label_chars),
    ]


def _side_panel(mode_label: str, span: int) -> list:
    return [
        f"{_BOLD}{mode_label.upper()} TIME GRAPH{_RESET}",
        f"last {span} days",
        "time vs. days",
    ]
