# Part 4 — persistent station + BEB

## Report output files

| File | Purpose |
|------|---------|
| **`part4_results.csv`** | Main data for the writeup (run `./aloha`) |
| **`part4_system_delay.png`** | System D vs λ (persistent vs Part-3-style BEB) |
| **`part4_system_throughput.png`** | System S vs λ |
| **`part4_persist_vs_other_delay.png`** | Station 0 vs average of other stations |

```bash
make && ./aloha
python3 plot_part4.py
```

CSV columns (see header): each row is either `persistent` (station 0 zero backoff) or `beb_baseline` (Part 3, no persistent station). Compare the same `arrival_rate` and `seed`.

- **`persistent_mean_delay` / `persistent_throughput`**: station 0  
- **`other_mean_delay` / `other_mean_throughput`**: stations 1–9 average  
- **`delay_ratio_persist_over_other`**: &lt; 1 means persistent station is faster  

Sweep uses `SWEEP_RUNLENGTH` (1M). For final numbers set `cfg.runlength = RUNLENGTH` in `main.c`.

Seeds: `lab_seeds.h` — `400440917`, `400473040`, `333333`, `222222`.
