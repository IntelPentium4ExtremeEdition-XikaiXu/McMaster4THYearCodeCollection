import csv
import os
import re
from pathlib import Path

OLD_CSV = "avg_CPI.csv"
OUT_CSV = "avg_CPI_improved.csv"

# Map output file prefix -> column name in avg_CPI.csv
bench_map = {
    "median": "median",
    "memBW": "memBW",
    "memcpy": "memcpy",
    "memlatency": "memlatency",
    "mergesort": "mergesort",
    "multiply": "multiply",
    "qsort": "qsort",
    "rsort": "rsort",
    "spmv": "spmv",
    "st-matmul": "stmatmul",
    "st-vvadd": "stvvadd",
    "towers": "towers",
    "vvadd": "vvadd",
}

def parse_raw_out(path):
    """Parse the last 'Finished' line from a macsim output file.
       Returns (instructions, cycles)."""
    text = Path(path).read_text(errors="ignore")
    pat = re.compile(r"insts:\s*(\d+)\s+cycles:\s*(\d+)")
    last = None
    for line in text.splitlines():
        if "Finished:" in line:
            m = pat.search(line)
            if m:
                last = (int(m.group(1)), int(m.group(2)))
    if last is None:
        raise RuntimeError(f"No 'Finished' line found in {path}")
    return last

# Read the original CSV
with open(OLD_CSV, newline="") as f:
    rows = list(csv.reader(f))

header = rows[0]
col = {name: i for i, name in enumerate(header)}
out_rows = [r[:] for r in rows]

# Parse all *_improved.out.txt files
new_data = {}
for fname in os.listdir("."):
    if fname.endswith("_improved.out.txt"):
        key = fname[:-len("_improved.out.txt")]
        bench = bench_map.get(key, key)
        if bench in col:
            insts, cycles = parse_raw_out(fname)
            new_data[bench] = (insts, cycles)

# Update the relevant rows in the output CSV
for r in out_rows:
    if not r:
        continue
    row_name = r[0]
    if row_name == "Total Instructions":
        for bench, (insts, cycles) in new_data.items():
            r[col[bench]] = str(insts)
    elif row_name == "Total cycles":
        for bench, (insts, cycles) in new_data.items():
            r[col[bench]] = str(cycles)
    elif row_name == "CPI macsim":
        for bench, (insts, cycles) in new_data.items():
            r[col[bench]] = f"{cycles / insts:.6f}"

# --- Build summary rows ---
# Find old CPI and old CPI macsim rows
old_cpi_row = next((r for r in rows if r and r[0] == "CPI"), None)
old_cpi_macsim_row = next((r for r in rows if r and r[0] == "CPI macsim"), None)

# Prepare summary row labels
summary_labels = [
    "old CPI",
    "old CPI macsim",
    "new CPI macsim",
    "improvement vs old CPI %",
    "improvement vs old CPI macsim %",
]

# Initialize summary rows with the label and empty strings for all benchmarks
summary_rows = [[label] + [""] * (len(header) - 1) for label in summary_labels]

# Fill in summary data for each benchmark
for bench, (insts, cycles) in new_data.items():
    idx = col[bench]
    new_cpi = cycles / insts
    new_ipc = insts / cycles

    old_cpi = float(old_cpi_row[idx]) if old_cpi_row and old_cpi_row[idx] else None
    old_cpi_macsim = float(old_cpi_macsim_row[idx]) if old_cpi_macsim_row and old_cpi_macsim_row[idx] else None

    imp_vs_cpi = (old_cpi - new_cpi) / old_cpi * 100 if old_cpi else None
    imp_vs_cpi_macsim = (old_cpi_macsim - new_cpi) / old_cpi_macsim * 100 if old_cpi_macsim else None

    summary_rows[0][idx] = f"{old_cpi:.6f}" if old_cpi is not None else ""
    summary_rows[1][idx] = f"{old_cpi_macsim:.6f}" if old_cpi_macsim is not None else ""
    summary_rows[2][idx] = f"{new_cpi:.6f}"
    summary_rows[3][idx] = f"{imp_vs_cpi:.4f}" if imp_vs_cpi is not None else ""
    summary_rows[4][idx] = f"{imp_vs_cpi_macsim:.4f}" if imp_vs_cpi_macsim is not None else ""

# Append summary rows to the bottom
out_rows.extend(summary_rows)

# Write the final CSV
with open(OUT_CSV, "w", newline="") as f:
    csv.writer(f).writerows(out_rows)

print(f"Generated: {OUT_CSV}")
print("Format matches avg_CPI.csv: columns are benchmarks, rows are metrics.")
print("Summary rows are merged at the bottom:")
print("  old CPI, old CPI macsim, new CPI macsim,")
print("  improvement vs old CPI %, improvement vs old CPI macsim %")
print("The 'total UOPS' row is kept as-is because macsim output does not contain UOP breakdowns.")
