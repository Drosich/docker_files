#!/usr/bin/env python3
"""
Plot a percentage depth dose (PDD) from TOPAS CSV scorer output.

Usage:
    python plot_pdd.py DepthDose_kill.csv
    python plot_pdd.py DepthDose_kill.csv DepthDose_nokill.csv -o pdd.png

By default the beam is assumed to enter at the HIGH Z bin index (default
TOPAS BeamPosition, beam travelling towards -Z). Use --entrance low if your
beam enters at bin 0.
"""
import argparse
import re
import sys

import numpy as np
import matplotlib.pyplot as plt


def read_topas_csv(path):
    """Return (depth_cm, value, header_info) for a 1D Z-binned TOPAS CSV."""
    nz, dz, unit, quantity = None, None, "", "Value"
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                m = re.search(r"Z in (\d+) bins? of ([\d.eE+-]+) (\w+)", line)
                if m:
                    nz, dz, unit = int(m.group(1)), float(m.group(2)), m.group(3)
                m = re.match(r"#\s*(\w+)\s*\(\s*(.+?)\s*\)", line)
                if m and "Sum" in line:
                    quantity = f"{m.group(1)} ({m.group(2)})"
                continue
            rows.append([float(x) for x in line.split(",")])

    data = np.array(rows)
    if data.ndim != 2 or data.shape[1] < 4:
        sys.exit(f"{path}: expected columns ix, iy, iz, value")
    if nz is None or dz is None:
        sys.exit(f"{path}: could not find 'Z in N bins of W cm' in header")

    # Sum over X/Y bins in case the scorer has more than one
    iz = data[:, 2].astype(int)
    values = np.bincount(iz, weights=data[:, 3], minlength=nz)

    if unit == "mm":
        dz /= 10.0
    elif unit == "m":
        dz *= 100.0
    return values, nz, dz, quantity


def depth_axis(nz, dz, entrance):
    idx = np.arange(nz)
    if entrance == "high":
        idx = (nz - 1) - idx
    return (idx + 0.5) * dz  # bin centres, cm from entrance


def distal_depth(depth, pdd, level):
    """Depth beyond the peak where the PDD falls to `level` percent."""
    ipk = int(np.argmax(pdd))
    d, p = depth[ipk:], pdd[ipk:]
    below = np.where(p < level)[0]
    if len(below) == 0:
        return np.nan
    j = below[0]
    # linear interpolation between j-1 and j
    return np.interp(level, [p[j], p[j - 1]], [d[j], d[j - 1]])


def main():
    ap = argparse.ArgumentParser(description="Plot PDD from TOPAS CSV output")
    ap.add_argument("files", nargs="+", help="TOPAS CSV files")
    ap.add_argument("-o", "--output", default="pdd.png", help="output image (default pdd.png)")
    ap.add_argument("--entrance", choices=["high", "low"], default="high",
                    help="Z bin index where the beam enters (default: high)")
    ap.add_argument("--absolute", action="store_true",
                    help="plot absolute values instead of normalising to 100%% at the peak")
    args = ap.parse_args()

    fig, ax = plt.subplots(figsize=(8, 5))

    for path in args.files:
        values, nz, dz, quantity = read_topas_csv(path)
        depth = depth_axis(nz, dz, args.entrance)
        order = np.argsort(depth)
        depth, values = depth[order], values[order]

        pdd = 100.0 * values / values.max()
        r90 = distal_depth(depth, pdd, 90)
        r80 = distal_depth(depth, pdd, 80)
        peak = depth[np.argmax(pdd)]

        print(f"{path}")
        print(f"  total           : {values.sum():.6g} {quantity}")
        print(f"  peak depth      : {peak:.3f} cm")
        print(f"  distal R90      : {r90:.3f} cm")
        print(f"  distal R80      : {r80:.3f} cm")

        y = values if args.absolute else pdd
        ax.plot(depth, y, drawstyle="steps-mid", label=path)

    ax.set_xlabel("Depth (cm)")
    ax.set_ylabel(quantity if args.absolute else "Relative dose (%)")
    ax.set_title("Percentage depth dose")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(args.output, dpi=150)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()