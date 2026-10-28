"""Part 2 plots. Average the two seeds. Overlay classic pure-ALOHA S = G e^{-2G}."""
import csv
from collections import defaultdict

import math

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("results.csv", newline="")))
if not rows:
    raise SystemExit("Run ./aloha first.")

# (N, backoff, lambda) -> lists of D, S, G
buckets = defaultdict(lambda: {"d": [], "s": [], "g": []})
for r in rows:
    key = (int(r["stations"]), int(float(r["backoff"])), float(r["arrival_rate"]))
    buckets[key]["d"].append(float(r["mean_delay"]))
    buckets[key]["s"].append(float(r["throughput"]))
    buckets[key]["g"].append(float(r["aggregate_load_G"]))

def avg(vals):
    return sum(vals) / len(vals)

g_theory = [i * 0.01 for i in range(201)]
s_theory = [g * math.exp(-2.0 * g) for g in g_theory]

for n in (5, 10):
    keys_n = [k for k in buckets if k[0] == n]
    if not keys_n:
        print(f"Warning: no data for N={n}")
        continue
    backoffs = sorted({k[1] for k in keys_n})

    plt.figure()
    for b in backoffs:
        pts = sorted((k for k in keys_n if k[1] == b), key=lambda k: k[2])
        plt.plot(
            [k[2] for k in pts],
            [avg(buckets[k]["s"]) for k in pts],
            marker="o",
            linestyle="-",
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
    for b in backoffs:
        pts = sorted((k for k in keys_n if k[1] == b), key=lambda k: avg(buckets[k]["s"]))
        plt.plot(
            [avg(buckets[k]["s"]) for k in pts],
            [avg(buckets[k]["d"]) for k in pts],
            marker="o",
            linestyle="-",
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
    plt.plot(g_theory, s_theory, "k--", label="theory S=G exp(-2G)")
    for b in backoffs:
        pts = sorted((k for k in keys_n if k[1] == b), key=lambda k: avg(buckets[k]["g"]))
        plt.plot(
            [avg(buckets[k]["g"]) for k in pts],
            [avg(buckets[k]["s"]) for k in pts],
            marker="o",
            linestyle="-",
            label=f"backoff={b}",
        )
    plt.xlabel("Aggregate load G")
    plt.ylabel("Throughput S")
    plt.title(f"Part 2: S vs G ({n} stations)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"throughput_vs_G_N{n}.png", dpi=160)

print("Wrote throughput_N5/N10.png, delay_vs_throughput_N5/N10.png, throughput_vs_G_N5/N10.png")
