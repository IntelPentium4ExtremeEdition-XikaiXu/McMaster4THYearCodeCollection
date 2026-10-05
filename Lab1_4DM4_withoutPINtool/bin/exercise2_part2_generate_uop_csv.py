import os
import re
import csv
from collections import Counter

DEBUG_DIR = "../labs/part2_debug"
OUTPUT_FILE = "../labs/UOP_No.csv"

benchmarks = [
    "median",
    "memBW",
    "memcpy",
    "memlatency",
    "mergesort",
    "multiply",
    "qsort",
    "rsort",
    "spmv",
    "stmatmul",
    "stvvadd",
    "towers",
    "vvadd"
]

pattern = re.compile(r"uop_type_name:(UOP_[A-Za-z0-9_]+)")

counts = {}
all_uops = set()

for benchmark in benchmarks:
    filename = os.path.join(
        DEBUG_DIR,
        f"{benchmark}_done_execution.debug"
    )

    print(f"Processing {benchmark}...")

    counter = Counter()

    with open(filename, "r", errors="ignore") as f:
        for line in f:
            match = pattern.search(line)

            if match:
                uop = match.group(1)

                # Ignore GPU UOPs
                if not uop.startswith("UOP_GPU"):
                    counter[uop] += 1
                    all_uops.add(uop)

    counts[benchmark] = counter


# Sort UOP names
all_uops = sorted(all_uops)

with open(OUTPUT_FILE, "w", newline="") as f:
    writer = csv.writer(f, delimiter=";")

    # Header
    writer.writerow(["UOP"] + benchmarks)

    # UOP counts
    for uop in all_uops:
        row = [uop]

        for benchmark in benchmarks:
            row.append(counts[benchmark].get(uop, 0))

        writer.writerow(row)

    # Total UOPs
    total_row = ["total UOPS"]

    for benchmark in benchmarks:
        total_row.append(sum(counts[benchmark].values()))

    writer.writerow(total_row)

print(f"\nDone. CSV saved to: {OUTPUT_FILE}")
