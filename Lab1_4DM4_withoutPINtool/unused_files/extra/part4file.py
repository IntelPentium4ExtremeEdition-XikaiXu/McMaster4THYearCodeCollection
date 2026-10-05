#!/usr/bin/env python3

import csv
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

BIN_DIR = Path(__file__).resolve().parent
ROOT_DIR = BIN_DIR.parent

LATENCY_FILE = ROOT_DIR / "def" / "uoplatency_x86.def"
EXEC_FILE = ROOT_DIR / "src" / "exec.cc"

TRACE_FILE_LIST = BIN_DIR / "trace_file_list"
MACSIM_FILE = BIN_DIR / "macsim"

PART3_FILE = BIN_DIR / "avg_CPI.csv"
PART4_FILE = BIN_DIR / "avg_CPI_improved.csv"

RESULT_FILE = BIN_DIR / "macsim_results_improved.csv"
LOG_DIR = BIN_DIR / "part4_logs"


# ============================================================
# Experiment settings
# ============================================================

GROUP_NUMBER = 6

FACTOR = (
    (GROUP_NUMBER + 55) * 10.0 / 110.0
)

ORIGINAL_TARGET_LATENCY = 10

NEW_LATENCY = max(
    1,
    round(ORIGINAL_TARGET_LATENCY / FACTOR)
)


# You said trace_file_list uses:
#
# 1../tools/benchmarks/median/BM.txt
#
# If MacSim reports "cannot open trace", change this to:
#
# TRACE_PREFIX = ""
#
TRACE_PREFIX = "1"


# ============================================================
# Benchmark groups
# ============================================================

IADD_BENCHMARKS = [
    "median",
    "memcpy",
    "mergesort",
    "multiply",
    "spmv",
    "st-matmul",
    "st-vvadd",
    "towers",
    "vvadd",
    "memlatency",
]


IMEM_BENCHMARKS = [
    "qsort",
    "rsort" ,
    "memBW"
]


ALL_BENCHMARKS = [
    "median",
    "memBW",
    "memcpy",
    "memlatency",
    "mergesort",
    "multiply",
    "qsort",
    "rsort",
    "spmv",
    "st-matmul",
    "st-vvadd",
    "towers",
    "vvadd"
]


TOP_UOP = {}

for benchmark in IADD_BENCHMARKS:
    TOP_UOP[benchmark] = "UOP_IADD"

for benchmark in IMEM_BENCHMARKS:
    TOP_UOP[benchmark] = "UOP_IMEM"


# ============================================================
# Original latency map
# ============================================================

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


# ============================================================
# Basic helper functions
# ============================================================

def stop(message):

    print("")
    print("ERROR:", message)
    print("")

    sys.exit(1)


def run_command(command, directory, output_file=None):

    print("")
    print("Running:", " ".join(command))

    if output_file is None:

        result = subprocess.run(
            command,
            cwd=str(directory)
        )

    else:

        with open(output_file, "w") as file:

            result = subprocess.run(
                command,
                cwd=str(directory),
                stdout=file,
                stderr=subprocess.STDOUT
            )

    if result.returncode != 0:

        stop(
            "Command failed: "
            + " ".join(command)
        )


# ============================================================
# Change one UOP latency
# ============================================================

def replace_latency(text, uop_name, latency):

    pattern = (
        r"(DEFUOP\(\s*"
        + re.escape(uop_name)
        + r"\s*,\s*)"
        + r"[-+]?\d+"
        + r"(\s*\))"
    )

    replacement = (
        r"\g<1>"
        + str(latency)
        + r"\g<2>"
    )

    new_text, number_changed = re.subn(
        pattern,
        replacement,
        text
    )

    if number_changed != 1:

        stop(
            "Expected exactly one definition for {}, found {}."
            .format(
                uop_name,
                number_changed
            )
        )

    return new_text


def configure_latency(original_text, target_uop):

    # Always start with original content.

    text = original_text

    # Make sure both target UOPs start at 10.

    text = replace_latency(
        text,
        "UOP_IADD",
        10
    )

    text = replace_latency(
        text,
        "UOP_IMEM",
        10
    )

    # Improve only the selected UOP.

    text = replace_latency(
        text,
        target_uop,
        NEW_LATENCY
    )

    LATENCY_FILE.write_text(text)

    # exec.cc includes uoplatency_x86.def.
    # Touching exec.cc forces recompilation.

    os.utime(
        str(EXEC_FILE),
        None
    )

    print("")
    print(
        "{} latency changed to {}."
        .format(
            target_uop,
            NEW_LATENCY
        )
    )


# ============================================================
# Build MacSim
# ============================================================

def build_macsim():

    print("")
    print("==============================")
    print("Building MacSim")
    print("==============================")

    run_command(
        [
            sys.executable,
            "build.py",
            "--debug"
        ],
        ROOT_DIR
    )

    if not MACSIM_FILE.exists():

        stop(
            "MacSim binary was not generated."
        )


# ============================================================
# Modify trace_file_list
# ============================================================

def write_trace_file(benchmark):

    trace_path = (
        TRACE_PREFIX
        + "../tools/benchmarks/"
        + benchmark
        + "/BM.txt"
    )

    with open(
        TRACE_FILE_LIST,
        "w"
    ) as file:

        file.write(trace_path)
        file.write("\n")

    print("")
    print(
        "trace_file_list ->",
        trace_path
    )


# ============================================================
# Extract MacSim result
# ============================================================

def extract_result(log_file):

    with open(
        log_file,
        "r",
        errors="ignore"
    ) as file:

        lines = file.readlines()

    core_total_line = None

    for line in lines:

        if "Core_Total" in line:
            core_total_line = line

    if core_total_line is None:

        stop(
            "Core_Total result not found in "
            + str(log_file)
        )

    match = re.search(
        r"insts:\s*(\d+)\s+cycles:\s*(\d+)",
        core_total_line
    )

    if match is None:

        stop(
            "Cannot extract instructions and cycles from: "
            + core_total_line
        )

    instructions = int(match.group(1))
    cycles = int(match.group(2))

    return instructions, cycles


# ============================================================
# Run one benchmark
# ============================================================

def run_benchmark(benchmark):

    write_trace_file(benchmark)

    log_file = (
        LOG_DIR
        / (benchmark + "_improved.out")
    )

    print("")
    print("==============================")
    print("Running:", benchmark)
    print("==============================")

    run_command(
        [str(MACSIM_FILE)],
        BIN_DIR,
        log_file
    )

    instructions, cycles = extract_result(
        log_file
    )

    print("")
    print("Benchmark:", benchmark)
    print("Instructions:", instructions)
    print("Cycles:", cycles)

    return instructions, cycles


# ============================================================
# CSV helper functions
# ============================================================

def detect_delimiter(filename):

    with open(
        filename,
        "r",
        errors="ignore"
    ) as file:

        first_line = file.readline()

    if ";" in first_line:
        return ";"

    return ","


def clean_benchmark_name(name):

    name = name.strip()

    suffix = "_execution_summary.txt"

    if name.endswith(suffix):

        name = name[:-len(suffix)]

    return name


# ============================================================
# Read avg_CPI.csv
# ============================================================

def read_part3_file():

    if not PART3_FILE.exists():

        stop(
            "avg_CPI.csv was not found in bin."
        )

    delimiter = detect_delimiter(
        PART3_FILE
    )

    with open(
        PART3_FILE,
        "r",
        newline="",
        errors="ignore"
    ) as file:

        reader = csv.reader(
            file,
            delimiter=delimiter
        )

        rows = list(reader)

    if len(rows) == 0:

        stop(
            "avg_CPI.csv is empty."
        )

    benchmarks = []

    for value in rows[0][1:]:

        value = value.strip()

        if value != "":

            benchmarks.append(
                clean_benchmark_name(value)
            )

    uop_rows = []

    for row in rows[1:]:

        if len(row) == 0:
            continue

        uop_name = row[0].strip()

        if not uop_name.startswith("UOP_"):
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
                count = int(float(value))

            counts.append(count)

        # Remove rows that are zero everywhere.

        if sum(counts) > 0:

            uop_rows.append(
                [uop_name] + counts
            )

    return delimiter, benchmarks, uop_rows


# ============================================================
# Generate improved CSV files
# ============================================================

def generate_csv(results):

    delimiter, benchmarks, uop_rows = (
        read_part3_file()
    )

    for benchmark in benchmarks:

        if benchmark not in results:

            stop(
                "Missing simulation result for "
                + benchmark
            )

    # --------------------------------------------------------
    # macsim_results_improved.csv
    # --------------------------------------------------------

    with open(
        RESULT_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(
            file,
            delimiter=delimiter
        )

        header = ["UOP"]

        for benchmark in benchmarks:

            header.append(
                benchmark
                + "_execution_summary.txt"
            )

        writer.writerow(header)

        instruction_row = ["Instructions"]
        cycle_row = ["Cycles"]

        for benchmark in benchmarks:

            instruction_row.append(
                results[benchmark]["instructions"]
            )

            cycle_row.append(
                results[benchmark]["cycles"]
            )

        writer.writerow(instruction_row)
        writer.writerow(cycle_row)

    # --------------------------------------------------------
    # Calculate improved CPI
    # --------------------------------------------------------

    total_uops = {}
    weighted_latency = {}

    for benchmark in benchmarks:

        total_uops[benchmark] = 0
        weighted_latency[benchmark] = 0

    for row in uop_rows:

        uop_name = row[0]

        if uop_name not in LATENCY:

            stop(
                "No latency found for "
                + uop_name
            )

        for index in range(len(benchmarks)):

            benchmark = benchmarks[index]
            count = row[index + 1]

            latency = LATENCY[uop_name]

            # Each benchmark gets only its own top UOP improved.

            if uop_name == TOP_UOP[benchmark]:

                latency = NEW_LATENCY

            total_uops[benchmark] += count

            weighted_latency[benchmark] += (
                count * latency
            )

    calculated_cpi = {}
    macsim_cpi = {}

    for benchmark in benchmarks:

        calculated_cpi[benchmark] = (
            float(weighted_latency[benchmark])
            / float(total_uops[benchmark])
        )

        instructions = (
            results[benchmark]["instructions"]
        )

        cycles = (
            results[benchmark]["cycles"]
        )

        macsim_cpi[benchmark] = (
            float(cycles)
            / float(instructions)
        )

    # --------------------------------------------------------
    # avg_CPI_improved.csv
    # --------------------------------------------------------

    with open(
        PART4_FILE,
        "w",
        newline=""
    ) as file:

        writer = csv.writer(
            file,
            delimiter=delimiter
        )

        writer.writerow(
            ["UOP"] + benchmarks
        )

        for row in uop_rows:
            writer.writerow(row)

        output_row = ["total UOPS"]

        for benchmark in benchmarks:

            output_row.append(
                total_uops[benchmark]
            )

        writer.writerow(output_row)

        output_row = ["CPI"]

        for benchmark in benchmarks:

            output_row.append(
                "{:.6f}".format(
                    calculated_cpi[benchmark]
                )
            )

        writer.writerow(output_row)

        output_row = ["Total Instructions"]

        for benchmark in benchmarks:

            output_row.append(
                results[benchmark]["instructions"]
            )

        writer.writerow(output_row)

        output_row = ["Total cycles"]

        for benchmark in benchmarks:

            output_row.append(
                results[benchmark]["cycles"]
            )

        writer.writerow(output_row)

        output_row = ["CPI macsim"]

        for benchmark in benchmarks:

            output_row.append(
                "{:.6f}".format(
                    macsim_cpi[benchmark]
                )
            )

        writer.writerow(output_row)


# ============================================================
# Main
# ============================================================

def main():

    required_files = [
        LATENCY_FILE,
        EXEC_FILE,
        TRACE_FILE_LIST,
        MACSIM_FILE,
        PART3_FILE
    ]

    for filename in required_files:

        if not filename.exists():

            stop(
                "Required file is missing: "
                + str(filename)
            )

    LOG_DIR.mkdir(
        exist_ok=True
    )

    backup_file = Path(
        str(LATENCY_FILE)
        + ".part4_backup"
    )

    shutil.copy2(
        LATENCY_FILE,
        backup_file
    )

    original_text = (
        backup_file.read_text()
    )

    results = {}

    print("")
    print("Group number:", GROUP_NUMBER)
    print("Improvement factor:", FACTOR)
    print("New integer latency:", NEW_LATENCY)

    try:

        # ----------------------------------------------------
        # Batch 1: IADD
        # ----------------------------------------------------

        print("")
        print("################################")
        print("Batch 1: UOP_IADD")
        print("################################")

        configure_latency(
            original_text,
            "UOP_IADD"
        )

        #build_macsim()

        for benchmark in IADD_BENCHMARKS:

            #instructions, cycles = (
                #run_benchmark(benchmark)
            #)

            results[benchmark] = {
                "instructions": instructions,
                "cycles": cycles
            }



        generate_csv(results)

        print("")
        print("================================")
        print("Part 4 complete")
        print("================================")
        print("")
        print("Generated:")
        print(RESULT_FILE)
        print(PART4_FILE)
        print("")
        print("Logs:")
        print(LOG_DIR)



if __name__ == "__main__":
     main()
