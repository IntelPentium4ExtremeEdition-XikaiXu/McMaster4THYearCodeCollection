# Part 1

Fixed arrival rate. Lambda does not change.

| Settings | Values |
|----------|--------|
| Model | M/D/1, FCFS |
| Packet length | 500 bits |
| Link bit rate | 1 Mbps (`10^6` b/s) |
| Packet transmission time | 0.5 ms |
| Arrival rate λ | **0.10** (fixed, packets per Tx time) |
| Seeds | 400440917, 400473040, 114514, 1919810 |
| Stations | 10 and 5 |
| Backoff | N=10: 5, 10, 20; N=5: 3, 5, 7 |
| Runs | **24** = 4 seeds × 6 configs |

Constants: `part1_appendix_a.h`.

```bash
make && ./aloha
python3 plot_part1.py
```

`part1_results.csv` has 24 rows. Plots are **D vs backoff** at that fixed λ: `part1_delay_N5.png`, `part1_delay_N10.png`.
