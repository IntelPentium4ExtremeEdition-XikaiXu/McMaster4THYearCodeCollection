#!/usr/bin/env python3

import csv
import sys


PART2_FILE = "UOP_No.csv"
RESULT_FILE = "macsim_results.csv"
OUTPUT_FILE = "avg_CPI.csv"


# Latency values from uoplatency_x86.txt
LATENCY = {
    "UOP_INV": 10,
    "UOP_NOP": 10,

    "UOP_CF": 10,
    "UOP_CMOV": 10,
    "UOP_LDA": 10,
    "UOP_IMEM": 10,
    "UOP_LD": 10,
    "UOP_ST": 10,

    "UOP_IADD": 10,
    "UOP_IMUL": 10,
    "UOP_IDIV": 10,
    "UOP_ICMP": 10,
    "UOP_LOGIC": 10,
    "UOP_SHIFT": 10,
    "UOP_BYTE": 10,
    "UOP_MM": 10,

    "UOP_FMEM": 10,

    "UOP_VADD": 1,
    "UOP_VSTR": 1,
    "UOP_VFADD": 1,

    "UOP_AES": 1,
    "UOP_PCLMUL": 1,
    "UOP_X87": 1,
    "UOP_XSAVE": 1,
    "UOP_XSAVEOPT": 1,

    "UOP_LFENCE": 100,
    "UOP_FULL_FENCE": 100,
    "UOP_ACQ_FENCE": 100,
    "UOP_REL_FENCE": 100,

    "UOP_FCF": 1,
    "UOP_FCVT": 2,
    "UOP_FADD": 2,
    "UOP_FMUL": 2,
    "UOP_FDIV": 8,
    "UOP_FCMP": 2,
    "UOP_FBIT": 2,
    "UOP_FCMOV": 1,

    "UOP_SSE": 1
}


def detect_delimiter(filename):
    with open(filename, "r", errors="ignore") as file:
        first_line = file.readline()

    if ";" in first_line:
        return ";"

    return ","


def clean_benchmark_name(name):
    """
    Make benchmark names easier to match.

    Example:
    median_execution_summary.txt -> median
    """

    name = name.strip()

    suffix = "_execution_summary.txt"

    if name.endswith(suffix):
        name = name[:-len(suffix)]

    return name


def read_part2_file(filename):
    """
    Read UOP_No.csv.

    Return:
        delimiter
        benchmark names
        nonzero UOP rows
    """

    delimiter = detect_delimiter(filename)

    try:
        with open(filename, "r", newline="", errors="ignore") as file:
            reader = csv.reader(file, delimiter=delimiter)
            rows = list(reader)

    except FileNotFoundError:
        print("Error: cannot find {}".format(filename))
        sys.exit(1)

    if len(rows) == 0:
        print("Error: {} is empty.".format(filename))
        sys.exit(1)

    header = rows[0]

    benchmarks = []

    for value in header[1:]:
        value = value.strip()

        if value != "":
            benchmarks.append(clean_benchmark_name(value))

    ignored_rows = [
        "TOTAL",
        "TOTAL UOPS",
        "TOTAL_UOPS",
        "INSTRUCTIONS",
        "CYCLES",
        "CPI",
        "TOTAL INSTRUCTIONS",
        "TOTAL CYCLES",
        "CPI MACSIM"
    ]

    useful_rows = []

    for row in rows[1:]:

        if len(row) == 0:
            continue

        uop_name = row[0].strip()

        if uop_name == "":
            continue

        if uop_name.upper() in ignored_rows:
            continue

        counts = []

        for index in range(len(benchmarks)):

            column = index + 1

            if column >= len(row):
                value = "0"
            else:
                value = row[column].strip()

            if value == "":
                count = 0
            else:
                try:
                    count = int(float(value))

                except ValueError:
                    print(
                        "Error: invalid count '{}' for {}.".format(
                            value,
                            uop_name
                        )
                    )
                    sys.exit(1)

            counts.append(count)

        # Remove UOP only if it is zero for every benchmark.
        if sum(counts) > 0:
            useful_rows.append([uop_name] + counts)

    return delimiter, benchmarks, useful_rows


def read_horizontal_results(filename):
    """
    Read this format:

    UOP,benchmark1,benchmark2,...
    Instructions,100,200,...
    Cycles,500,900,...
    """

    delimiter = detect_delimiter(filename)

    try:
        with open(filename, "r", newline="", errors="ignore") as file:
            reader = csv.reader(file, delimiter=delimiter)
            rows = list(reader)

    except FileNotFoundError:
        print("Error: cannot find {}".format(filename))
        sys.exit(1)

    if len(rows) < 3:
        print("Error: {} requires at least 3 rows.".format(filename))
        sys.exit(1)

    header = rows[0]

    instruction_row = None
    cycle_row = None

    for row in rows[1:]:

        if len(row) == 0:
            continue

        row_name = row[0].strip().upper()

        if row_name in ["INSTRUCTIONS", "TOTAL INSTRUCTIONS"]:
            instruction_row = row

        elif row_name in ["CYCLES", "TOTAL CYCLES"]:
            cycle_row = row

    if instruction_row is None:
        print("Error: Instructions row not found.")
        sys.exit(1)

    if cycle_row is None:
        print("Error: Cycles row not found.")
        sys.exit(1)

    results = {}

    # Start at column 1 because column 0 contains row labels.
    for column in range(1, len(header)):

        original_name = header[column].strip()

        # Ignore empty columns at the end.
        if original_name == "":
            continue

        benchmark = clean_benchmark_name(original_name)

        if column >= len(instruction_row):
            print(
                "Error: missing Instructions value for {}".format(
                    benchmark
                )
            )
            sys.exit(1)

        if column >= len(cycle_row):
            print(
                "Error: missing Cycles value for {}".format(
                    benchmark
                )
            )
            sys.exit(1)

        instruction_text = instruction_row[column].strip()
        cycle_text = cycle_row[column].strip()

        if instruction_text == "" or cycle_text == "":
            print(
                "Error: empty Instructions or Cycles for {}".format(
                    benchmark
                )
            )
            sys.exit(1)

        try:
            instructions = int(float(instruction_text))
            cycles = int(float(cycle_text))

        except ValueError:
            print(
                "Error: invalid Instructions or Cycles for {}".format(
                    benchmark
                )
            )
            sys.exit(1)

        results[benchmark] = {
            "instructions": instructions,
            "cycles": cycles
        }

    return results


# ------------------------------------------------------------
# Read files
# ------------------------------------------------------------

delimiter, benchmarks, uop_rows = read_part2_file(PART2_FILE)

macsim_results = read_horizontal_results(RESULT_FILE)


print("")
print("Benchmarks in Part 2:")

for benchmark in benchmarks:
    print("  {}".format(benchmark))


print("")
print("Benchmarks in MacSim results:")

for benchmark in macsim_results:
    print("  {}".format(benchmark))


# ------------------------------------------------------------
# Check benchmark matching
# ------------------------------------------------------------

for benchmark in benchmarks:

    if benchmark not in macsim_results:
        print("")
        print(
            "Error: '{}' is missing from {}.".format(
                benchmark,
                RESULT_FILE
            )
        )
        print("")
        sys.exit(1)


# ------------------------------------------------------------
# Initialize results
# ------------------------------------------------------------

total_uops = {}
weighted_latency = {}
calculated_cpi = {}
macsim_cpi = {}


for benchmark in benchmarks:
    total_uops[benchmark] = 0
    weighted_latency[benchmark] = 0


# ------------------------------------------------------------
# Calculate total UOP count and weighted latency
# ------------------------------------------------------------

for row in uop_rows:

    uop_name = row[0]

    if uop_name not in LATENCY:
        print("")
        print(
            "Error: no latency found for {}.".format(
                uop_name
            )
        )
        print("This UOP has a nonzero count.")
        print("")
        sys.exit(1)

    latency = LATENCY[uop_name]

    for index in range(len(benchmarks)):

        benchmark = benchmarks[index]
        count = row[index + 1]

        total_uops[benchmark] += count
        weighted_latency[benchmark] += count * latency


# ------------------------------------------------------------
# Calculate CPI
# ------------------------------------------------------------

for benchmark in benchmarks:

    if total_uops[benchmark] == 0:
        calculated_cpi[benchmark] = 0.0
    else:
        calculated_cpi[benchmark] = (
            float(weighted_latency[benchmark])
            / float(total_uops[benchmark])
        )

    instructions = macsim_results[benchmark]["instructions"]
    cycles = macsim_results[benchmark]["cycles"]

    if instructions <= 0:
        print(
            "Error: Instructions must be positive for {}.".format(
                benchmark
            )
        )
        sys.exit(1)

    macsim_cpi[benchmark] = (
        float(cycles) / float(instructions)
    )


# ------------------------------------------------------------
# Write avg_CPI.csv
# ------------------------------------------------------------

with open(OUTPUT_FILE, "w", newline="") as file:

    writer = csv.writer(file, delimiter=delimiter)

    writer.writerow(["UOP"] + benchmarks)

    # Write only UOP rows that are used.
    for row in uop_rows:
        writer.writerow(row)

    # Total UOP count.
    output_row = ["total UOPS"]

    for benchmark in benchmarks:
        output_row.append(total_uops[benchmark])

    writer.writerow(output_row)

    # Calculated average CPI.
    output_row = ["CPI"]

    for benchmark in benchmarks:
        output_row.append(
            "{:.6f}".format(calculated_cpi[benchmark])
        )

    writer.writerow(output_row)

    # Total instructions.
    output_row = ["Total Instructions"]

    for benchmark in benchmarks:
        output_row.append(
            macsim_results[benchmark]["instructions"]
        )

    writer.writerow(output_row)

    # Total cycles.
    output_row = ["Total cycles"]

    for benchmark in benchmarks:
        output_row.append(
            macsim_results[benchmark]["cycles"]
        )

    writer.writerow(output_row)

    # MacSim CPI.
    output_row = ["CPI macsim"]

    for benchmark in benchmarks:
        output_row.append(
            "{:.6f}".format(macsim_cpi[benchmark])
        )

    writer.writerow(output_row)


# ------------------------------------------------------------
# Print summary
# ------------------------------------------------------------

print("")
print("Part 3 complete.")
print("Created: {}".format(OUTPUT_FILE))
print("")

for benchmark in benchmarks:

    print("Benchmark: {}".format(benchmark))

    print(
        "  Total UOPs: {}".format(
            total_uops[benchmark]
        )
    )

    print(
        "  Weighted latency: {}".format(
            weighted_latency[benchmark]
        )
    )

    print(
        "  Calculated CPI: {:.6f}".format(
            calculated_cpi[benchmark]
        )
    )

    print(
        "  Total Instructions: {}".format(
            macsim_results[benchmark]["instructions"]
        )
    )

    print(
        "  Total Cycles: {}".format(
            macsim_results[benchmark]["cycles"]
        )
    )

    print(
        "  MacSim CPI: {:.6f}".format(
            macsim_cpi[benchmark]
        )
    )

    print("")
