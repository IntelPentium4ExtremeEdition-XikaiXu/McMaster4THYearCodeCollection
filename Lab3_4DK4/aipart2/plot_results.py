import csv
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("results.csv", newline="")))

for n in sorted({int(r["stations"]) for r in rows}):
    subset = [r for r in rows if int(r["stations"]) == n]
    plt.figure()
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
    plt.xlabel("Arrival rate lambda")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 2: D vs lambda ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"delay_N{n}.png", dpi=160)

    plt.figure()
    for b in sorted({int(r["backoff"]) for r in subset}):
        pts = sorted(
            (r for r in subset if int(r["backoff"]) == b),
            key=lambda r: float(r["arrival_rate"]),
        )
        plt.plot(
            [float(r["arrival_rate"]) for r in pts],
            [float(r["throughput"]) for r in pts],
            marker="o",
            label=f"backoff={b}",
        )
    plt.xlabel("Arrival rate lambda")
    plt.ylabel("Throughput S")
    plt.title(f"Part 2: S vs lambda ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"throughput_N{n}.png", dpi=160)

    plt.figure()
    for b in sorted({int(r["backoff"]) for r in subset}):
        pts = sorted(
            (r for r in subset if int(r["backoff"]) == b),
            key=lambda r: float(r["throughput"]),
        )
        plt.plot(
            [float(r["throughput"]) for r in pts],
            [float(r["mean_delay"]) for r in pts],
            marker="o",
            label=f"backoff={b}",
        )
    plt.xlabel("Throughput S")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 2: D vs S ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"delay_vs_throughput_N{n}.png", dpi=160)

    plt.figure()
    for b in sorted({int(r["backoff"]) for r in subset}):
        pts = sorted(
            (r for r in subset if int(r["backoff"]) == b),
            key=lambda r: float(r["aggregate_load_G"]),
        )
        plt.plot(
            [float(r["aggregate_load_G"]) for r in pts],
            [float(r["throughput"]) for r in pts],
            marker="o",
            label=f"backoff={b}",
        )
    plt.xlabel("Aggregate load G")
    plt.ylabel("Throughput S")
    plt.title(f"Part 2: S vs G ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"throughput_vs_G_N{n}.png", dpi=160)

print("Wrote Part 2 PNG plots (delay, throughput, D-S, S-G).")
