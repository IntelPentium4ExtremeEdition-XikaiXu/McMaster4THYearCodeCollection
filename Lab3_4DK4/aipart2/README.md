# Part 2

PDF Section 2.2: **λ is swept** (unlike Part 1). Same six (N, backoff) pairs.

| Item | Value |
|------|--------|
| N, backoff | 10: 5/10/20; 5: 3/5/7 |
| λ | 0.05 … 0.40 (8 values) |
| Seeds | 400440917, 400473040, 114514, 1919810 |
| Runs | 192 = 4 × 6 × 8 |
| Backoff | fixed mean (`2 U(0,1) mean_backoff`) |
| S | successes / simulation time |
| G | transmission starts / simulation time |

```bash
make && ./aloha
python3 plot_results.py
```

Plots: `throughput_N*.png` (S–λ), `delay_vs_throughput_N*.png` (D–S), `throughput_vs_G_N*.png` (S–G + theoretical `S = G e^{-2G}`).
