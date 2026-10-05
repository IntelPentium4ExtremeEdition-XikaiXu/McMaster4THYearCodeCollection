from pathlib import Path

code = r'''#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


# ============================================================
# Paths
# ============================================================

BIN_DIR = Path(__file__).resolve().parent
MACSIM_FILE = BIN_DIR / "macsim"
TRACE_FILE_LIST = BIN_DIR / "trace_file_list"


# ============================================================
# Benchmark order
# ============================================================

BENCHMARKS = [
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
    "qsort",
    "rsort",
    "memBW",
]


# ============================================================
# Trace configuration
# ============================================================

# Keep the same prefix behavior as the original script.
TRACE_PREFIX = "1"


# ============================================================
# Basic helper
# ============================================================

def stop(message):
    print("")
    print("ERROR:", message)
    print("")
    sys.exit(1)


def run_command(command, directory):
    print("")
    print("Running:", " ".join(command))
    print("")

    result = subprocess.run(
        command,
        cwd=str(directory)
    )

    if result.returncode != 0:
        stop(
            "Command failed: "
            + " ".join(command)
        )


# ============================================================
# Change only trace_file_list
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
# Run one benchmark
# ============================================================

def run_benchmark(benchmark, number, total):
    print("")
    print("########################################")
    print(
        "Benchmark {}/{}: {}".format(
            number,
            total,
            benchmark
        )
    )
    print("########################################")

    write_trace_file(benchmark)

    run_command(
        [str(MACSIM_FILE)],
        BIN_DIR
    )


# ============================================================
# Main
# ============================================================

def main():

    # Only check the files required to trigger MacSim.
    if not MACSIM_FILE.exists():
        stop(
            "MacSim binary was not found: "
            + str(MACSIM_FILE)
        )

    if not TRACE_FILE_LIST.exists():
        stop(
            "trace_file_list was not found: "
            + str(TRACE_FILE_LIST)
        )

    print("")
    print("========================================")
    print("Part 4 - Trigger Only")
    print("========================================")
    print("")
    print("Latency modification : NONE")
    print("exec.cc modification : NONE")
    print("MacSim build         : NONE")
    print("CPI calculation      : NONE")
    print("CSV generation       : NONE")
    print("")
    print(
        "The existing MacSim binary will be used."
    )
    print(
        "Only trace_file_list is changed "
        "between benchmarks."
    )
    print("")

    total = len(BENCHMARKS)

    for number, benchmark in enumerate(
        BENCHMARKS,
        start=1
    ):
        run_benchmark(
            benchmark,
            number,
            total
        )

    print("")
    print("========================================")
    print("All benchmarks completed")
    print("========================================")
    print("")


if __name__ == "__main__":
    main()
'''

out = Path("/mnt/data/part4_trigger_only.py")
out.write_text(code, encoding="utf-8")
print(f"Created: {out}")
