import csv
import os
import re

UOP_FILE = "../labs/UOP_No.csv"
LATENCY_FILE = "../def/uoplatency_x86.def"
DEBUG_DIR = "../labs/part2_debug"
OUTPUT_FILE = "../labs/avg_CPI.csv"

# -------------------------------
# Read UOP latencies
# -------------------------------

latencies = {}

latency_pattern = re.compile(
    r"DEFUOP\s*\(\s*(UOP_[A-Za-z0-9_]+)\s*,\s*(\d+)"
)

with open(LATENCY_FILE, "r") as f:
    for line in f:
        match = latency_pattern.search(line)

        if match:
            uop = match.group(1)
            latency = int(match.group(2))
            latencies[uop] = latency


print("Loaded UOP latencies:")
for uop, latency in latencies.items():
    print(f"{uop}: {latency}")


# -------------------------------
# Read UOP_No.csv
# -------------------------------

with open(UOP_FILE, "r") as f:
    reader = list(csv.reader(f, delimiter=";"))

header = reader[0]
benchmarks = header[1:]

uop_rows = []
total_uops = {}

for row in reader[1:]:

    if row[0] == "total UOPS":
        for i, benchmark in enumerate(benchmarks):
            total_uops[benchmark] = int(row[i + 1])
    else:
        uop_rows.append(row)


# -------------------------------
# Calculate manual CPI
# -------------------------------

manual_cpi = {}

for i, benchmark in enumerate(benchmarks):

    total_cycles_from_uops = 0

    for row in uop_rows:

        uop = row[0]
        count = int(row[i + 1])

        if uop not in latencies:
            print(f"WARNING: No latency found for {uop}")
            continue

        total_cycles_from_uops += count * latencies[uop]

    manual_cpi[benchmark] = (
        total_cycles_from_uops / total_uops[benchmark]
    )


# -------------------------------
# Extract MacSim instructions/cycles
# -------------------------------

# -------------------------------
# Extract MacSim instructions/cycles
# -------------------------------

instructions = {}
cycles = {}
macsim_cpi = {}

pattern = re.compile(
    r"Core_Total\s+Finished:\s+"
    r"insts:(\d+)\s+cycles:(\d+)"
)

def read_tail(filename, max_bytes=65536):
    """
    Read only the last part of a large file.
    Core_Total is printed near the end of MacSim output.
    """
    with open(filename, "rb") as f:
        f.seek(0, os.SEEK_END)
        file_size = f.tell()

        start = max(0, file_size - max_bytes)
        f.seek(start)

        return f.read().decode("utf-8", errors="ignore")


for benchmark in benchmarks:

    filename = os.path.join(
        DEBUG_DIR,
        f"{benchmark}_execution.debug"
    )

    text = read_tail(filename)

    matches = pattern.findall(text)

    if not matches:
        print(f"ERROR: Could not find result for {benchmark}")
        continue

    inst, cyc = matches[-1]

    instructions[benchmark] = int(inst)
    cycles[benchmark] = int(cyc)

    macsim_cpi[benchmark] = (
        cycles[benchmark] / instructions[benchmark]
    )

    print(
        f"{benchmark}: "
        f"instructions={instructions[benchmark]}, "
        f"cycles={cycles[benchmark]}, "
        f"CPI={macsim_cpi[benchmark]:.4f}"
    )
    
# -------------------------------
# Write avg_CPI.csv
# -------------------------------

with open(OUTPUT_FILE, "w", newline="") as f:

    writer = csv.writer(f, delimiter=";")

    # Original UOP table
    for row in reader:
        writer.writerow(row)

    # Manual CPI
    writer.writerow(
        ["CPI"] +
        [f"{manual_cpi[b]:.4f}" for b in benchmarks]
    )

    # MacSim instructions
    writer.writerow(
        ["Total_Instructions"] +
        [instructions[b] for b in benchmarks]
    )

    # MacSim cycles
    writer.writerow(
        ["Total_cycles"] +
        [cycles[b] for b in benchmarks]
    )

    # MacSim CPI
    writer.writerow(
        ["CPI_macsim"] +
        [f"{macsim_cpi[b]:.4f}" for b in benchmarks]
    )


print(f"\nDone. Output saved to {OUTPUT_FILE}")
