# Part 4 — persistent station + BEB

PDF: one station retransmits in the next slot (no backoff). Compare **delay and throughput** of that station vs the others.

| Item | Value |
|------|--------|
| Seeds | 400440917, 400473040, 114514, 1919810 |
| Stations | 10; station **0** is persistent |
| Others | BEB on `[0, 2^Nc)` |
| Baseline | all stations BEB (`beb_baseline`) |
| λ | 0.05 … 0.40 (8 values) |
| Runs | **64** = 4 × 8 × 2 |

```bash
make && ./aloha
python3 plot_part4.py
```

| File | Use in report |
|------|----------------|
| `part4_results.csv` | tables |
| `part4_persist_vs_other_delay.png` | station 0 vs others (D) — main Part 4 figure |
| `part4_persist_vs_other_throughput.png` | station 0 vs others (S) |
| `part4_system_delay.png` / `part4_system_throughput.png` | vs Part 3 BEB baseline |
