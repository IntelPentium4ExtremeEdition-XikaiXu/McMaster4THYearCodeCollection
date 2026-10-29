#!/usr/bin/env python3
"""Part 4 diagrams from part4_results.csv.

The lab asks for the persistent station's mean delay and throughput
compared with the other stations. Each seed is a separate line through
its points, sorted by λ.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "part4_results.csv"


def load(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows and "live_packets" in rows[0]:
        rows = [
            row for row in rows
            if int(row["successes"]) >= 10000000 and int(row["live_packets"]) <= 1000
        ]
    return rows


def series(rows, stations):
    chosen = [row for row in rows if int(row["stations"]) == stations]
    chosen.sort(key=lambda row: (float(row["lambda"]), int(row["seed"])))
    return chosen


def panel(ax, rows, xkey, y_persistent, y_other, ylabel, log_y):
    styles = (
        (5, "o", "s", "C0", "C1"),
        (10, "^", "D", "C2", "C3"),
    )
    for stations, persist_marker, other_marker, persist_color, other_color in styles:
        chosen = series(rows, stations)
        for index, seed in enumerate(sorted({row["seed"] for row in chosen})):
            one = sorted(
                (row for row in chosen if row["seed"] == seed),
                key=lambda row: float(row[xkey]),
            )
            x = [float(row[xkey]) for row in one]
            ax.plot(
                x,
                [float(row[y_persistent]) for row in one],
                marker=persist_marker,
                linestyle="-",
                color=persist_color,
                markersize=6,
                label=f"N = {stations}, station 0 (persistent)" if index == 0 else None,
            )
            ax.plot(
                x,
                [float(row[y_other]) for row in one],
                marker=other_marker,
                linestyle="-",
                color=other_color,
                markerfacecolor="none",
                markeredgecolor=other_color,
                markersize=7,
                label=f"N = {stations}, other stations (mean)" if index == 0 else None,
                zorder=4,
            )
    ax.set_xscale("log")
    ax.set_xlabel("Aggregate arrival rate λ (packets per packet transmission time)")
    ax.set_ylabel(ylabel)
    if log_y:
        ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.35)
    ax.legend(fontsize=8)


def main():
    if not CSV_PATH.is_file():
        raise SystemExit(f"Missing {CSV_PATH}. Run ./aloha in Part4 first.")

    rows = load(CSV_PATH)

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    panel(
        ax,
        rows,
        "lambda",
        "persistent_delay",
        "other_mean_delay",
        "Mean delay D (packet transmission times)",
        True,
    )
    ax.set_title("Part 4: delay of the persistent station and the other stations")
    fig.tight_layout()
    delay_out = HERE / "part4_delay_vs_lambda.png"
    fig.savefig(delay_out, dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.4, 5.4))
    panel(
        ax,
        rows,
        "lambda",
        "persistent_throughput",
        "other_mean_throughput",
        "Per-station throughput (successful packets per packet transmission time)",
        False,
    )
    ax.set_title("Part 4: throughput of the persistent station and the other stations")
    fig.tight_layout()
    throughput_out = HERE / "part4_throughput_vs_lambda.png"
    fig.savefig(throughput_out, dpi=160)
    plt.close(fig)

    print(f"Wrote {delay_out}")
    print(f"Wrote {throughput_out}")


if __name__ == "__main__":
    main()
