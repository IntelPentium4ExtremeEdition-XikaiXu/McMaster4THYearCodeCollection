#!/bin/bash

BENCH_DIR="../tools/benchmarks"
TRACE_LIST="trace_file_list"
OUT_DIR="../labs/part2_debug"

mkdir -p "$OUT_DIR"

benchmarks=(
    median
    memBW
    memcpy
    memlatency
    mergesort
    multiply
    qsort
    rsort
    spmv
    stmatmul
    stvvadd
    towers
    vvadd
)

for b in "${benchmarks[@]}"; do

    case "$b" in
        stmatmul)
            dir_name="st-matmul"
            ;;
        stvvadd)
            dir_name="st-vvadd"
            ;;
        *)
            dir_name="$b"
            ;;
    esac

    echo "Running $b using directory $dir_name..."

    printf "1\n%s\n" \
        "$BENCH_DIR/$dir_name/BM.txt" \
        > "$TRACE_LIST"

    ./macsim &> "$OUT_DIR/${b}_execution.debug"

    grep "done_exec" \
        "$OUT_DIR/${b}_execution.debug" \
        &> "$OUT_DIR/${b}_done_execution.debug"

    echo "$b finished."

done

echo "All benchmarks finished."
