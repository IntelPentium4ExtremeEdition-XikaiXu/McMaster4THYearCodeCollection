LAB_ROOT="/home/gp06/Desktop/macsim-4dm4/4DM4_Lab1Template-main"

    lab_checked=0

    printf '%-14s %-10s %-10s\n' "Benchmark" "Config" "Raw"

    for lab_dir in "$LAB_ROOT"/tools/benchmarks/*; do
        [ -f "$lab_dir/BM" ] || continue

        lab_config="MISSING"
        lab_raw="MISSING"

        if [ -s "$lab_dir/BM.txt" ]; then
            lab_config="OK"
        fi

        for lab_file in "$lab_dir"/BM*.raw*; do
            if [ -s "$lab_file" ]; then
                lab_raw="OK"
            fi
        done

        printf '%-14s %-10s %-10s\n' \
            "${lab_dir##*/}" "$lab_config" "$lab_raw"

        lab_checked=$((lab_checked + 1))
    done

    printf '\nBenchmarks checked: %s\n' "$lab_checked"