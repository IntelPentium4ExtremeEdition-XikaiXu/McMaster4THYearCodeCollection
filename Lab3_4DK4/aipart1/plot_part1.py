import csv
from collections import defaultdict

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("part1_results.csv", newline="")))
if not rows:
    raise SystemExit("Run ./aloha first.")

# Average the two seeds. Lambda is fixed; x-axis is mean backoff.
buckets = defaultdict(list)
lam = float(rows[0]["arrival_rate"])
for r in rows:
    buckets[(int(r["stations"]), int(float(r["backoff"])))].append(float(r["mean_delay"]))

written = []
for n, title_backoffs in ((10, "5, 10, 20"), (5, "3, 5, 7")):
    pts = sorted((k for k in buckets if k[0] == n), key=lambda k: k[1])
    if not pts:
        print(f"Warning: no N={n} rows")
        continue
    plt.figure()
    plt.plot(
        [k[1] for k in pts],
        [sum(buckets[k]) / len(buckets[k]) for k in pts],
        marker="o",
    )
    plt.xlabel("Mean backoff duration")
    plt.ylabel("Mean delay D")
    plt.title(f"Part 1: D vs backoff (N={n}, lambda={lam:g})")
    plt.grid(True)
    plt.tight_layout()
    out = f"part1_delay_N{n}.png"
    plt.savefig(out, dpi=160)
    written.append(out)

print("Wrote " + ", ".join(written))
