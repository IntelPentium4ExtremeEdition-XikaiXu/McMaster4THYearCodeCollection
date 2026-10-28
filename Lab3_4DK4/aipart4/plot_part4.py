"""Part 4 plots: average 4 seeds, connect markers."""
import csv
from collections import defaultdict

import matplotlib.pyplot as plt

rows = list(csv.DictReader(open("part4_results.csv", newline="")))
if not rows:
    raise SystemExit("Run ./aloha first.")


def avg_by_lambda(mode):
    buckets = defaultdict(lambda: {"d": [], "s": [], "dp": [], "do": [], "sp": [], "so": []})
    for row in rows:
        if row["mode"] != mode:
            continue
        lam = float(row["arrival_rate"])
        buckets[lam]["d"].append(float(row["system_mean_delay"]))
        buckets[lam]["s"].append(float(row["system_throughput"]))
        if row["persistent_mean_delay"]:
            buckets[lam]["dp"].append(float(row["persistent_mean_delay"]))
            buckets[lam]["do"].append(float(row["other_mean_delay"]))
            buckets[lam]["sp"].append(float(row["persistent_throughput"]))
            buckets[lam]["so"].append(float(row["other_mean_throughput"]))
    out = []
    for lam in sorted(buckets):
        b = buckets[lam]
        out.append(
            {
                "lam": lam,
                "d": sum(b["d"]) / len(b["d"]),
                "s": sum(b["s"]) / len(b["s"]),
                "dp": sum(b["dp"]) / len(b["dp"]) if b["dp"] else None,
                "do": sum(b["do"]) / len(b["do"]) if b["do"] else None,
                "sp": sum(b["sp"]) / len(b["sp"]) if b["sp"] else None,
                "so": sum(b["so"]) / len(b["so"]) if b["so"] else None,
            }
        )
    return out


persist = avg_by_lambda("persistent")
baseline = avg_by_lambda("beb_baseline")

plt.figure()
plt.plot([x["lam"] for x in persist], [x["d"] for x in persist],
         marker="o", linestyle="-", label="persistent (system)")
plt.plot([x["lam"] for x in baseline], [x["d"] for x in baseline],
         marker="s", linestyle="-", label="BEB baseline (system)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Mean delay D")
plt.title("Part 4: system mean delay")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_system_delay.png", dpi=160)

plt.figure()
plt.plot([x["lam"] for x in persist], [x["s"] for x in persist],
         marker="o", linestyle="-", label="persistent (system)")
plt.plot([x["lam"] for x in baseline], [x["s"] for x in baseline],
         marker="s", linestyle="-", label="BEB baseline (system)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Throughput S")
plt.title("Part 4: system throughput")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_system_throughput.png", dpi=160)

plt.figure()
plt.plot([x["lam"] for x in persist], [x["dp"] for x in persist],
         marker="o", linestyle="-", label="station 0 (persistent)")
plt.plot([x["lam"] for x in persist], [x["do"] for x in persist],
         marker="s", linestyle="-", label="other stations (avg)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Mean delay D")
plt.title("Part 4: persistent station vs others (delay)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_persist_vs_other_delay.png", dpi=160)

plt.figure()
plt.plot([x["lam"] for x in persist], [x["sp"] for x in persist],
         marker="o", linestyle="-", label="station 0 (persistent)")
plt.plot([x["lam"] for x in persist], [x["so"] for x in persist],
         marker="s", linestyle="-", label="other stations (avg)")
plt.xlabel("Arrival rate lambda")
plt.ylabel("Throughput S")
plt.title("Part 4: persistent station vs others (throughput)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("part4_persist_vs_other_throughput.png", dpi=160)

print(
    "Wrote part4_system_delay.png, part4_system_throughput.png, "
    "part4_persist_vs_other_delay.png, part4_persist_vs_other_throughput.png"
)
