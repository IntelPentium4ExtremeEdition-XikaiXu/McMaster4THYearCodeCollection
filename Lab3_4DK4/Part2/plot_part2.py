#!/usr/bin/env python3
"""Part 2: throughput S versus λ, delay D versus S, and S versus offered load G.

Each seed is a separate line through its points, sorted along the x-axis.
The pure-ALOHA curve S = G e^{-2G} is the lecture formula. A row is kept
when the run reached 10 million successes and at most 1000 packets were
still queued.
"""

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "part2_results.csv"

MARKERS = {3: "v", 5: "^", 7: "D", 10: "P", 20: "X"}
PANELS = ((5, (3, 5, 7)), (10, (5, 10, 20)))


def load(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [
        row for row in rows
        if int(row["successes"]) >= 10000000 and int(row["live_packets"]) <= 1000
    ]


def scatter_config(ax, rows, stations, backoffs, xkey, ykey):
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
                key=lambda row: float(row[xkey]),
            )
            line, = ax.plot(
                [float(row[xkey]) for row in one],
                [float(row[ykey]) for row in one],
                marker=MARKERS[backoff],
                linestyle="-",
                color=color,
                markersize=6,
                label=f"mean backoff {backoff}, each seed" if color is None else None,
            )
            color = line.get_color()


def main():
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing {CSV_PATH}. Run ./aloha in Part2 first.")

    rows = load(CSV_PATH)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    for ax, (stations, backoffs) in zip(axes, PANELS):
        chosen_lams = [
            float(row["lambda"]) for row in rows
            if int(row["stations"]) == stations
        ]
        lo = min(chosen_lams) / 1.35
        hi = max(chosen_lams) * 1.35
        ax.plot([lo, hi], [lo, hi], color="0.45", linestyle="--", linewidth=1,
                label="S = λ", zorder=1)
        scatter_config(ax, rows, stations, backoffs, "lambda", "throughput")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_xlabel("Aggregate arrival rate λ (packets per packet transmission time)")
        ax.set_title(f"N = {stations}")
        ax.grid(True, which="both", alpha=0.35)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Throughput S (successful packets per packet transmission time)")
    fig.suptitle("Part 2: throughput versus arrival rate")
    fig.tight_layout()
    out_s = HERE / "part2_S_vs_lambda.png"
    fig.savefig(out_s, dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    for ax, (stations, backoffs) in zip(axes, PANELS):
        scatter_config(ax, rows, stations, backoffs, "throughput", "mean_delay")
        ax.set_yscale("log")
        ax.set_xlabel("Throughput S (successful packets per packet transmission time)")
        ax.set_title(f"N = {stations}")
        ax.grid(True, which="both", alpha=0.35)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Mean delay D (packet transmission times)")
    fig.suptitle("Part 2: mean delay versus throughput")
    fig.tight_layout()
    out_d = HERE / "part2_D_vs_S.png"
    fig.savefig(out_d, dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    theory_g = [i / 200 for i in range(0, 201)]
    theory_s = [g * math.exp(-2.0 * g) for g in theory_g]
    for ax, (stations, backoffs) in zip(axes, PANELS):
        ax.plot(theory_g, theory_s, color="black", linestyle="--", linewidth=1,
                label="pure ALOHA  S = G e^{-2G}", zorder=1)
        scatter_config(ax, rows, stations, backoffs, "aggregate_load_G", "throughput")
        ax.set_xlabel("Offered load G (transmission attempts per packet transmission time)")
        ax.set_title(f"N = {stations}")
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 0.35)
        ax.grid(True, alpha=0.35)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Throughput S (successful packets per packet transmission time)")
    fig.suptitle("Part 2: throughput versus offered load")
    fig.tight_layout()
    out_g = HERE / "part2_S_vs_G.png"
    fig.savefig(out_g, dpi=160)
    plt.close(fig)

    print(f"Wrote {out_s}")
    print(f"Wrote {out_d}")
    print(f"Wrote {out_g} ({len(rows)} steady points)")


if __name__ == "__main__":
    main()
