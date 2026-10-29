"""Command-line interface for terminal-plots."""
import argparse
import csv
import sys

from .core import bar_chart, boxplot, histogram, scatter, sparkline


def _floats(vals):
    out = []
    for v in vals:
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="terminal-plots", description="Plot CSV columns in the terminal.")
    ap.add_argument("kind", choices=["hist", "bar", "spark", "box", "scatter"])
    ap.add_argument("csvfile", help="CSV file, or - for one number per line on stdin")
    ap.add_argument("-c", "--column", help="value column")
    ap.add_argument("-g", "--group", help="group column (box plot)")
    ap.add_argument("-x", help="x column (scatter)")
    ap.add_argument("-b", "--bins", default="auto")
    ap.add_argument("-w", "--width", type=int, default=40)
    ap.add_argument("--top", type=int)
    ap.add_argument("--ascii", action="store_true", help="ASCII characters only")
    args = ap.parse_args(argv)

    if args.csvfile == "-":
        rows = [{"value": l.strip()} for l in sys.stdin if l.strip()]
        args.column = "value"
    else:
        with open(args.csvfile, encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    col = args.column or next(iter(rows[0]))
    if args.kind == "hist":
        bins = "auto" if args.bins == "auto" else int(args.bins)
        print(histogram(_floats(r[col] for r in rows), bins, args.width, args.ascii))
    elif args.kind == "bar":
        print(bar_chart([r[col] for r in rows if r[col]], args.width, args.ascii, top=args.top))
    elif args.kind == "spark":
        vals = _floats(r[col] for r in rows)
        print("%s  min=%g max=%g last=%g" % (sparkline(vals, args.ascii), min(vals), max(vals), vals[-1]))
    elif args.kind == "box":
        groups = {}
        for r in rows:
            v = _floats([r[col]])
            if v:
                groups.setdefault(r[args.group] if args.group else col, []).append(v[0])
        print(boxplot(groups, max(args.width, 30)))
    else:
        pairs = [(a, b) for a, b in ((_floats([r[args.x]]), _floats([r[col]])) for r in rows) if a and b]
        print(scatter([a[0] for a, _ in pairs], [b[0] for _, b in pairs], max(args.width, 30)))
    return 0
