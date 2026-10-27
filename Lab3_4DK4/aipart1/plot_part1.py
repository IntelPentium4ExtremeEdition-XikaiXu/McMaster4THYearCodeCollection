import csv
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("part1_results.csv", newline="")))
for n in sorted({int(r["stations"]) for r in rows}):
    plt.figure()
    subset = [r for r in rows if int(r["stations"]) == n]
    for b in sorted({int(r["backoff"]) for r in subset}):
        pts = sorted(
            (r for r in subset if int(r["backoff"]) == b),
            key=lambda r: float(r["arrival_rate"]),
        )
        plt.plot(
            [float(r["arrival_rate"]) for r in pts],
            [float(r["mean_delay"]) for r in pts],
            marker="o",
            label=f"backoff={b}",
        )
    plt.xlabel("Arrival rate lambda (per station)")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 1: D vs lambda ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"part1_delay_N{n}.png", dpi=160)

print("Wrote part1_delay_N5.png and part1_delay_N10.png")
