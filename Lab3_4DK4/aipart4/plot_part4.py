"""Part 4 lab report plots from part4_results.csv."""
import csv
from collections import defaultdict

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("part4_results.csv", newline="")))

# Average over seeds for each (mode, lambda).
def avg_by_lambda(mode):
    buckets = defaultdict(lambda: {"d": [], "s": [], "dp": [], "do": []})
    for row in rows:
        if row["mode"] != mode:
            continue
        lam = float(row["arrival_rate"])
        buckets[lam]["d"].append(float(row["system_mean_delay"]))
        buckets[lam]["s"].append(float(row["system_throughput"]))
        if row["persistent_mean_delay"]:
            buckets[lam]["dp"].append(float(row["persistent_mean_delay"]))
            buckets[lam]["do"].append(float(row["other_mean_delay"]))
    out = []
    for lam in sorted(buckets):
        b = buckets[lam]
        out.append(
            (
                lam,
                sum(b["d"]) / len(b["d"]),
                sum(b["s"]) / len(b["s"]),
                sum(b["dp"]) / len(b["dp"]) if b["dp"] else None,
                sum(b["do"]) / len(b["do"]) if b["do"] else None,
            )
        )
    return out

persist = avg_by_lambda("persistent")
baseline = avg_by_lambda("beb_baseline")

plt.figure()
plt.plot([x[0] for x in persist], [x[1] for x in persist], "o-", label="persistent (system)")
plt.plot([x[0] for x in baseline], [x[1] for x in baseline], "s-", label="BEB baseline (system)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Mean delay D")
plt.title("Part 4: system mean delay")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_system_delay.png", dpi=160)

plt.figure()
plt.plot([x[0] for x in persist], [x[2] for x in persist], "o-", label="persistent (system)")
plt.plot([x[0] for x in baseline], [x[2] for x in baseline], "s-", label="BEB baseline (system)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Throughput S")
plt.title("Part 4: system throughput")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_system_throughput.png", dpi=160)

plt.figure()
plt.plot([x[0] for x in persist], [x[3] for x in persist], "o-", label="station 0 (persistent)")
plt.plot([x[0] for x in persist], [x[4] for x in persist], "s-", label="other stations (avg)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Mean delay D")
plt.title("Part 4: persistent station vs others (delay)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_persist_vs_other_delay.png", dpi=160)

print(
    "Wrote part4_system_delay.png, part4_system_throughput.png, "
    "part4_persist_vs_other_delay.png"
)
