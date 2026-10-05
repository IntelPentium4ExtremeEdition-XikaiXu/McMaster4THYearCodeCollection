set -euo pipefail

cd "$PIN_HOME"

printf 'benchmark_name;instruction_count\n' \
    > "$LAB_OUT/lab1-exercise1-inscount.csv"

for lab_bm in "$LAB_ROOT"/tools/benchmarks/*/BM; do
    [ -f "$lab_bm" ] || continue

    lab_name=$(basename "$(dirname "$lab_bm")")
    lab_result="$LAB_TMP/${lab_name}_inscount.out"

    ./pin \
      -t source/tools/ManualExamples/obj-intel64/inscount0.so \
      -o "$lab_result" \
      -- "$lab_bm"

    lab_count=$(awk '$1 == "Count" {print $2; exit}' "$lab_result")

    if [[ ! "$lab_count" =~ ^[0-9]+$ ]]; then
        printf 'Invalid instruction count: %s\n' "$lab_name" >&2
        exit 1
    fi

    printf '%s;%s\n' "$lab_name" "$lab_count" \
        >> "$LAB_OUT/lab1-exercise1-inscount.csv"
done