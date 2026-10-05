#!/usr/bin/env python3

import os
import re
import subprocess
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

BIN_DIR = Path(__file__).resolve().parent
ROOT_DIR = BIN_DIR.parent

EXEC_FILE = ROOT_DIR / "src" / "exec.cc"

TRACE_FILE_LIST = BIN_DIR / "trace_file_list"
MACSIM_FILE = BIN_DIR / "macsim"

LOG_DIR = BIN_DIR / "part4_logs"


# ============================================================
# Experiment settings
# ============================================================

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
    "vvadd"
    #"memlatency",
]

IMEM_BENCHMARKS = [
    "qsort",
    "rsort"
    #"memBW",
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
    "vvadd",
]

# Change this to IADD_BENCHMARKS or IMEM_BENCHMARKS if needed.
BENCHMARKS = IADD_BENCHMARKS 


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
# Trigger recompile
# ============================================================

def trigger_recompile():

    print("")
    print("==============================")
    print("Triggering recompilation")
    print("==============================")

    # exec.cc includes uoplatency_x86.def.
    # Touching exec.cc forces recompilation.
    os.utime(
        str(EXEC_FILE),
        None
    )

    print("")
    print("Touched:", EXEC_FILE)


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
# Main
# ============================================================

def main():

    required_files = [
        EXEC_FILE,
        TRACE_FILE_LIST,
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

    results = {}

    trigger_recompile()
    build_macsim()

    for benchmark in BENCHMARKS:

        instructions, cycles = run_benchmark(benchmark)

        results[benchmark] = {
            "instructions": instructions,
            "cycles": cycles
        }

    print("")
    print("==============================")
    print("Summary")
    print("==============================")

    for benchmark in BENCHMARKS:

        print(
            "{}: instructions={} cycles={}".format(
                benchmark,
                results[benchmark]["instructions"],
                results[benchmark]["cycles"]
            )
        )

    print("")
    print("==============================")
    print("Part 4 complete")
    print("==============================")
    print("")
    print("Logs:")
    print(LOG_DIR)


if __name__ == "__main__":
    main()
