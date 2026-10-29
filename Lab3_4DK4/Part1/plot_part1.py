#!/usr/bin/env python3
"""Part 1: mean delay D versus arrival rate.

The lab asks for D versus λ at N = 10 (backoff 5, 10, 20) and N = 5
(backoff 3, 5, 7). Each seed is a separate line through its points, sorted
by λ. A row is kept when the run reached 10 million successes and at most
1000 packets were still queued, so the mean is a steady-state value.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "part1_results.csv"

MARKERS = {3: "v", 5: "^", 7: "D", 10: "P", 20: "X"}
PANELS = ((5, (3, 5, 7)), (10, (5, 10, 20)))


def load(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row for row in rows
        if int(row["successes"]) >= 10000000 and int(row["live_packets"]) <= 1000
    ]


def main():
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing {CSV_PATH}. Run ./aloha in Part1 first.")

    rows = load(CSV_PATH)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    for ax, (stations, backoffs) in zip(axes, PANELS):
        for backoff in backoffs:
            chosen = [
                row for row in rows
                if int(row["stations"]) == stations
                and int(float(row["mean_backoff"])) == backoff
            ]
            color = None
            for seed in sorted({row["seed"] for row in chosen}):
                one = sorted(
                    (row for row in chosen if row["seed"] == seed),
                    key=lambda row: float(row["lambda"]),
                )
                line, = ax.plot(
                    [float(row["lambda"]) for row in one],
                    [float(row["mean_delay"]) for row in one],
                    marker=MARKERS[backoff],
                    linestyle="-",
                    color=color,
                    markersize=6,
                    label=f"mean backoff {backoff}, each seed" if color is None else None,
                )
                color = line.get_color()
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Aggregate arrival rate λ (packets per packet transmission time)")
        ax.set_title(f"N = {stations}")
        ax.grid(True, which="both", alpha=0.35)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Mean delay D (packet transmission times)")
    fig.suptitle("Part 1: mean delay versus arrival rate")
    fig.tight_layout()
    out = HERE / "part1_D_vs_lambda.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Wrote {out} ({len(rows)} steady points)")


if __name__ == "__main__":
    main()
