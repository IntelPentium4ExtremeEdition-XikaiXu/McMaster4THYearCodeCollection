# Part 1 — Simlib ALOHA (same core as `aipart4`)

Fixed mean backoff; sweeps all six (stations, backoff) pairs, eight arrival rates, and four seeds from `lab_seeds.h`.

```bash
make
./aloha          # writes part1_results.csv (uses SWEEP_RUNLENGTH)
python3 plot_part1.py
```

For final report numbers, increase `SWEEP_RUNLENGTH` or set `cfg.runlength = RUNLENGTH` in `main.c`.

Seeds: `400440917`, `400473040`, `333333`, `222222`.
