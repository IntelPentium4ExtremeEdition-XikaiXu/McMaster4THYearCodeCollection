import csv
import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("comparison.csv", newline="")))

for n in sorted({int(r["stations"]) for r in rows}):
    subset = [r for r in rows if int(r["stations"]) == n]
    plt.figure()
    for mode in ("fixed", "BEB"):
        pts = sorted(
            (r for r in subset if r["mode"] == mode),
            key=lambda r: float(r["throughput"]),
        )
        plt.plot(
            [float(r["throughput"]) for r in pts],
            [float(r["mean_delay"]) for r in pts],
            marker="o",
            label=mode,
        )
    plt.xlabel("Throughput S")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 3: D vs S ({n} stations, fixed backoff={subset[0]['fixed_backoff']})")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"part3_D_vs_S_N{n}.png", dpi=160)

    plt.figure()
    for mode in ("fixed", "BEB"):
        pts = sorted(
            (r for r in subset if r["mode"] == mode),
            key=lambda r: float(r["arrival_rate"]),
        )
        plt.plot(
            [float(r["arrival_rate"]) for r in pts],
            [float(r["mean_delay"]) for r in pts],
            marker="o",
            label=mode,
        )
    plt.xlabel("Arrival rate lambda")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 3: D vs lambda ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"part3_delay_vs_lambda_N{n}.png", dpi=160)

print("Wrote part3_D_vs_S_N5.png, part3_D_vs_S_N10.png, ...")
