#!/usr/bin/env python3
"""Part 3 diagrams from part3_results.csv.

The lab asks for mean delay D versus throughput S at 5 and 10 stations,
compared with the fixed-backoff D-versus-S curves from Part 2 when that
CSV is present. Each seed is a separate line through its points.
"""

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
PART3_CSV = HERE / "part3_results.csv"
PART2_CSV = HERE.parent / "Part2" / "part2_results.csv"


def load(path):
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows and "live_packets" in rows[0]:
        rows = [
            row for row in rows
            if int(row["successes"]) >= 10000000 and int(row["live_packets"]) <= 1000
        ]
    return rows


def scatter_beb(ax, rows, stations, marker, norm):
    chosen = [row for row in rows if int(row["stations"]) == stations]
    for seed in sorted({row["seed"] for row in chosen}):
        one = sorted(
            (row for row in chosen if row["seed"] == seed),
            key=lambda row: float(row["throughput"]),
        )
        ax.plot(
            [float(row["throughput"]) for row in one],
            [float(row["mean_delay"]) for row in one],
            color="0.45",
            linestyle="-",
            linewidth=1,
            zorder=2,
        )
    return ax.scatter(
        [float(row["throughput"]) for row in chosen],
        [float(row["mean_delay"]) for row in chosen],
        c=[float(row["lambda"]) for row in chosen],
        cmap="viridis",
        norm=norm,
        marker=marker,
        s=42,
        edgecolors="black",
        linewidths=0.4,
        zorder=3,
    )


def style_delay_throughput(ax, title):
    ax.set_xlabel("Throughput S (successful packets per packet transmission time)")
    ax.set_ylabel("Mean delay D (packet transmission times)")
    ax.set_yscale("log")
    ax.set_title(title)
    ax.grid(True, which="both", alpha=0.35)
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="0.45", linestyle="-",
               markeredgecolor="black", markerfacecolor="0.75",
               label="N = 5, each seed"),
        Line2D([0], [0], marker="s", color="0.45", linestyle="-",
               markeredgecolor="black", markerfacecolor="0.75",
               label="N = 10, each seed"),
    ])


def main():
    if not PART3_CSV.is_file():
        raise SystemExit(f"Missing {PART3_CSV}. Run ./aloha in Part3 first.")

    rows = load(PART3_CSV)
    lambdas = [float(row["lambda"]) for row in rows]
    norm = Normalize(vmin=min(lambdas), vmax=max(lambdas))
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    scatter_beb(ax, rows, 5, "o", norm)
    scatter_beb(ax, rows, 10, "s", norm)
    style_delay_throughput(
        ax,
        "Part 3: binary exponential backoff, D versus S",
    )
    colorbar = fig.colorbar(
        ScalarMappable(norm=norm, cmap="viridis"),
        ax=ax,
    )
    colorbar.set_label("Aggregate arrival rate λ (packets per packet transmission time)")
    fig.tight_layout()
    out = HERE / "part3_D_vs_S.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Wrote {out}")

    if not PART2_CSV.is_file():
        print(f"No {PART2_CSV}, so the Part 2 fixed-backoff comparison was not drawn.")
        return

    fixed = load(PART2_CSV)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0), sharey=True)
    backoff_markers = {
        3: "v",
        5: "^",
        7: "D",
        10: "P",
        20: "X",
    }
    for ax, stations in zip(axes, (5, 10)):
        beb = [row for row in rows if int(row["stations"]) == stations]
        labeled = False
        for seed in sorted({row["seed"] for row in beb}):
            one = sorted(
                (row for row in beb if row["seed"] == seed),
                key=lambda row: float(row["throughput"]),
            )
            ax.plot(
                [float(row["throughput"]) for row in one],
                [float(row["mean_delay"]) for row in one],
                marker="o",
                linestyle="-",
                color="black",
                markersize=5,
                label="BEB, each seed" if not labeled else None,
                zorder=3,
            )
            labeled = True
        backoffs = sorted({
            int(float(row["mean_backoff"]))
            for row in fixed
            if int(row["stations"]) == stations
        })
        for backoff in backoffs:
            chosen = [
                row for row in fixed
                if int(row["stations"]) == stations
                and int(float(row["mean_backoff"])) == backoff
            ]
            color = None
            for seed in sorted({row["seed"] for row in chosen}):
                one = sorted(
                    (row for row in chosen if row["seed"] == seed),
                    key=lambda row: float(row["throughput"]),
                )
                line, = ax.plot(
                    [float(row["throughput"]) for row in one],
                    [float(row["mean_delay"]) for row in one],
                    marker=backoff_markers.get(backoff, "x"),
                    linestyle="-",
                    color=color,
                    markersize=6,
                    label=f"fixed backoff {backoff}, each seed" if color is None else None,
                )
                color = line.get_color()
        ax.set_yscale("log")
        ax.set_xlabel("Throughput S (successful packets per packet transmission time)")
        ax.set_title(f"N = {stations}")
        ax.grid(True, which="both", alpha=0.35)
        ax.legend(fontsize=8)
    axes[0].set_ylabel("Mean delay D (packet transmission times)")
    fig.suptitle("Part 3: BEB compared with Part 2 fixed mean backoff")
    fig.tight_layout()
    out = HERE / "part3_D_vs_S_vs_fixed_backoff.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
