# Part 3 — binary exponential backoff

PDF: backoff uniform on `[0, 2^Nc)` packet times. Plot **D vs S** for 5 and 10 stations; compare with Part 2 fixed backoff.

| Item | Value |
|------|--------|
| Seeds | 400440917, 400473040, 114514, 1919810 |
| N | 5 (fixed backoff 5), 10 (fixed backoff 10) |
| Modes | `fixed` vs `BEB` |
| λ | 0.05 … 0.40 (8 values) |
| Runs | **128** = 4 × 2 × 2 × 8 |

```bash
make && ./aloha
python3 plot_comparison.py
```

Main figures: `part3_D_vs_S_N5.png`, `part3_D_vs_S_N10.png`.
