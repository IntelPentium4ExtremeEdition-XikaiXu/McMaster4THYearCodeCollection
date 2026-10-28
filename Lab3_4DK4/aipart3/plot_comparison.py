"""Part 3: average 4 seeds, connect markers. Primary plot is D vs S."""
import csv
from collections import defaultdict

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("comparison.csv", newline="")))
if not rows:
    raise SystemExit("Run ./aloha first.")

# (mode, N, lambda) -> D and S
buckets = defaultdict(lambda: {"d": [], "s": []})
for r in rows:
    key = (r["mode"], int(r["stations"]), float(r["arrival_rate"]))
    buckets[key]["d"].append(float(r["mean_delay"]))
    buckets[key]["s"].append(float(r["throughput"]))


def avg(vals):
    return sum(vals) / len(vals)


written = []
for n in (5, 10):
    keys_n = [k for k in buckets if k[1] == n]
    if not keys_n:
        print(f"Warning: no data for N={n}")
        continue

    plt.figure()
    for mode in ("fixed", "BEB"):
        pts = sorted((k for k in keys_n if k[0] == mode), key=lambda k: avg(buckets[k]["s"]))
        plt.plot(
            [avg(buckets[k]["s"]) for k in pts],
            [avg(buckets[k]["d"]) for k in pts],
            marker="o",
            linestyle="-",
            label=mode,
        )
    plt.xlabel("Throughput S")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 3: D vs S ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    out = f"part3_D_vs_S_N{n}.png"
    plt.savefig(out, dpi=160)
    written.append(out)

    plt.figure()
    for mode in ("fixed", "BEB"):
        pts = sorted((k for k in keys_n if k[0] == mode), key=lambda k: k[2])
        plt.plot(
            [k[2] for k in pts],
            [avg(buckets[k]["d"]) for k in pts],
            marker="o",
            linestyle="-",
            label=mode,
        )
    plt.xlabel("Arrival rate lambda")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 3: D vs lambda ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    out = f"part3_delay_vs_lambda_N{n}.png"
    plt.savefig(out, dpi=160)
    written.append(out)

print("Wrote " + ", ".join(written))
