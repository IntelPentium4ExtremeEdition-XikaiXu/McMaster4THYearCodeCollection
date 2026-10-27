# Part 3 — binary exponential backoff (Simlib core)

BEB: uniform backoff on `[0, 2^Nc)` packet transmission times (see `packet_transmission.c`).

Compares **fixed** vs **BEB** for 5 stations (backoff 5) and 10 stations (backoff 10), eight arrival rates, four seeds.

```bash
make && ./aloha
python3 plot_comparison.py
```

Primary lab plot: **D vs S** (`part3_D_vs_S_N5.png`, `part3_D_vs_S_N10.png`).
