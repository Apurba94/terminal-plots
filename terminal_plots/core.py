"""Text renderers. All functions return strings so they can be logged or embedded in reports."""
import math
import statistics
from collections import Counter

BLOCKS = " ▏▎▍▌▋▊▉█"
SPARKS = "▁▂▃▄▅▆▇█"


def _bar(value, maximum, width, ascii_only=False):
    if maximum <= 0:
        return ""
    cells = value / maximum * width
    if ascii_only:
        return "#" * int(round(cells))
    full = int(cells)
    frac = int(round((cells - full) * 8))
    if frac == 8:
        full, frac = full + 1, 0
    return "█" * full + (BLOCKS[frac] if frac else "")


def _fmt(x):
    return ("%.4g" % x) if isinstance(x, float) else str(x)


def histogram(values, bins=10, width=40, ascii_only=False, lo=None, hi=None):
    if not values:
        return "(no data)"
    lo = min(values) if lo is None else lo
    hi = max(values) if hi is None else hi
    if hi == lo:
        hi = lo + 1
    if bins == "auto":
        bins = max(1, math.ceil(math.log2(len(values)) + 1))   # Sturges' rule
    step = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        if lo <= v <= hi:
            counts[min(bins - 1, int((v - lo) / step))] += 1
    mx = max(counts)
    edges = [lo + i * step for i in range(bins + 1)]
    lab = [("[%s, %s%s" % (_fmt(edges[i]), _fmt(edges[i + 1]), "]" if i == bins - 1 else ")")) for i in range(bins)]
    w = max(len(l) for l in lab)
    lines = ["%s %s %d" % (l.rjust(w), _bar(c, mx, width, ascii_only).ljust(width), c) for l, c in zip(lab, counts)]
    s = statistics
    lines.append("n=%d mean=%s sd=%s median=%s" % (len(values), _fmt(s.fmean(values)),
                                                  _fmt(s.stdev(values)) if len(values) > 1 else "0", _fmt(s.median(values))))
    return "\n".join(lines)


def bar_chart(items, width=40, ascii_only=False, sort=True, top=None):
    """items: dict label -> value, or an iterable of labels (counted)."""
    if not isinstance(items, dict):
        items = Counter(items)
    pairs = sorted(items.items(), key=lambda kv: -kv[1]) if sort else list(items.items())
    if top:
        pairs = pairs[:top]
    if not pairs:
        return "(no data)"
    mx = max(v for _, v in pairs)
    w = max(len(str(k)) for k, _ in pairs)
    total = sum(items.values())
    return "\n".join("%s %s %s (%.1f%%)" % (str(k).rjust(w), _bar(v, mx, width, ascii_only).ljust(width), _fmt(v),
                                            100.0 * v / total if total else 0) for k, v in pairs)


def sparkline(values, ascii_only=False):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    chars = "_.-~^" if ascii_only else SPARKS
    if hi == lo:
        return chars[len(chars) // 2] * len(values)
    return "".join(chars[min(len(chars) - 1, int((v - lo) / (hi - lo) * len(chars)))] for v in values)


def boxplot(groups, width=50):
    """groups: dict name -> values. Draws whiskers (1.5 IQR), box (Q1-Q3), median '|' and outliers 'o'."""
    allv = [v for vs in groups.values() for v in vs]
    lo, hi = min(allv), max(allv)
    span = (hi - lo) or 1
    pos = lambda v: int(round((v - lo) / span * (width - 1)))
    w = max(len(str(k)) for k in groups)
    lines = []
    for name, vs in groups.items():
        vs = sorted(vs)
        q1, med, q3 = statistics.quantiles(vs, n=4, method="inclusive") if len(vs) > 1 else (vs[0],) * 3
        iqr = q3 - q1
        inside = [v for v in vs if q1 - 1.5 * iqr <= v <= q3 + 1.5 * iqr]
        row = [" "] * width
        for i in range(pos(inside[0]), pos(inside[-1]) + 1):
            row[i] = "-"
        for i in range(pos(q1), pos(q3) + 1):
            row[i] = "="
        row[pos(inside[0])] = row[pos(inside[-1])] = "+"
        row[pos(med)] = "|"
        for v in vs:
            if v not in inside:
                row[pos(v)] = "o"
        lines.append("%s %s  median=%s" % (str(name).rjust(w), "".join(row), _fmt(med)))
    lines.append("%s %s%s" % (" " * w, _fmt(lo).ljust(width - len(_fmt(hi))), _fmt(hi)))
    return "\n".join(lines)


def scatter(x, y, width=60, height=20):
    """Character scatter plot; denser cells use darker characters."""
    if not x:
        return "(no data)"
    x0, x1, y0, y1 = min(x), max(x), min(y), max(y)
    grid = [[0] * width for _ in range(height)]
    for a, b in zip(x, y):
        c = int((a - x0) / ((x1 - x0) or 1) * (width - 1))
        r = height - 1 - int((b - y0) / ((y1 - y0) or 1) * (height - 1))
        grid[r][c] += 1
    shades = " .:o#@"
    out = []
    for i, row in enumerate(grid):
        label = _fmt(y1) if i == 0 else _fmt(y0) if i == height - 1 else ""
        out.append("%8s |%s" % (label, "".join(shades[min(len(shades) - 1, n)] for n in row)))
    out.append(" " * 9 + "+" + "-" * width)
    out.append(" " * 10 + _fmt(x0).ljust(width - len(_fmt(x1))) + _fmt(x1))
    return "\n".join(out)
