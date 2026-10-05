#!/usr/bin/env python3

import os
import re
import csv

# =====================================================
# All UOP Types
# =====================================================

ALL_UOPS = [

    "UOP_INV",
    "UOP_SPEC",

    "UOP_NOP",

    "UOP_CF",
    "UOP_CMOV",
    "UOP_LDA",
    "UOP_IMEM",
    "UOP_IADD",
    "UOP_IMUL",
    "UOP_IDIV",
    "UOP_ICMP",
    "UOP_LOGIC",
    "UOP_SHIFT",
    "UOP_BYTE",
    "UOP_MM",

    "UOP_VADD",
    "UOP_VSTR",
    "UOP_VFADD",

    "UOP_LFENCE",
    "UOP_FULL_FENCE",
    "UOP_ACQ_FENCE",
    "UOP_REL_FENCE",

    "UOP_FMEM",

    "UOP_FCF",
    "UOP_FCVT",
    "UOP_FADD",
    "UOP_FMUL",
    "UOP_FDIV",
    "UOP_FCMP",
    "UOP_FBIT",
    "UOP_FCMOV",

    "UOP_LD",
    "UOP_ST",

    "UOP_SSE",

    "UOP_SIMD",

    "UOP_AES",
    "UOP_PCLMUL",
    "UOP_X87",
    "UOP_XSAVE",
    "UOP_XSAVEOPT"
]

# =====================================================
# Find Debug Files
# =====================================================

debug_files = []

for file in os.listdir("."):

    if file.endswith(".txt"):
        debug_files.append(file)

debug_files.sort()

if len(debug_files) == 0:
    print("No *_done_execution.debug files found.")
    exit()

# =====================================================
# Read Every Benchmark
# =====================================================

bench_data = {}

for filename in debug_files:

    benchmark = filename.replace(
        "_done_execution.debug",
        ""
    )

    print("Reading:", filename)

    # Initialize all UOPs with zero

    counts = {}

    for uop in ALL_UOPS:
        counts[uop] = 0

    # Open file

    with open(
        filename,
        "r",
        errors="ignore"
    ) as f:

        for line in f:

            match = re.search(
                r'uop_type_name:(UOP_[A-Z0-9_]+)',
                line
            )

            if match:

                uop = match.group(1)

                if uop in counts:
                    counts[uop] += 1

    bench_data[benchmark] = counts

# =====================================================
# Generate CSV
# =====================================================

benchmarks = sorted(bench_data.keys())

with open(
    "UOP_No.csv",
    "w",
    newline=""
) as csvfile:

    writer = csv.writer(csvfile)

    # Header

    header = ["UOP"]

    for bench in benchmarks:
        header.append(bench)

    writer.writerow(header)

    # UOP rows

    for uop in ALL_UOPS:

        row = [uop]

        for bench in benchmarks:

            row.append(
                bench_data[bench][uop]
            )

        writer.writerow(row)

    # TOTAL row

    total_row = ["TOTAL"]

    for bench in benchmarks:

        total = sum(
            bench_data[bench].values()
        )

        total_row.append(total)

    writer.writerow(total_row)

print()
print("Finished.")
print("Created: UOP_No.csv")
