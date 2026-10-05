#!/bin/bash

BENCH_DIR="../tools/benchmarks"
OUT_DIR="../labs/part4_imem"
TRACE_LIST="trace_file_list"

mkdir -p "$OUT_DIR"

benchmarks=(
    memBW
    memlatency
    qsort
    rsort
)

echo "benchmark;instructions;cycles;CPI" > "$OUT_DIR/imem_results.csv"

for b in "${benchmarks[@]}"; do

    echo "Running $b..."

    printf "1\n%s\n" \
        "$BENCH_DIR/$b/BM.txt" \
        > "$TRACE_LIST"

    ./macsim &> "$OUT_DIR/${b}_improved.out"

    line=$(grep "Core_Total.*Finished" \
        "$OUT_DIR/${b}_improved.out" | tail -1)

    inst=$(echo "$line" |
        sed -n 's/.*insts:\([0-9]*\).*/\1/p')

    cycles=$(echo "$line" |
        sed -n 's/.*cycles:\([0-9]*\).*/\1/p')

    cpi=$(awk -v c="$cycles" -v i="$inst" \
        'BEGIN {printf "%.4f", c/i}')

    echo "$b;$inst;$cycles;$cpi" \
        >> "$OUT_DIR/imem_results.csv"

    echo "$b finished: inst=$inst cycles=$cycles CPI=$cpi"

done

echo "Done."
