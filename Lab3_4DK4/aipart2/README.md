# Part 2 — throughput and load (Simlib core)

Same sweep as Part 1; CSV includes **S** and **G** (transmission attempts per unit time).

```bash
make && ./aloha
python3 plot_results.py
```

`G` is measured as total transmission starts divided by simulation time (packet-times per Tx time when packet duration is 1).

Seeds: see `lab_seeds.h`.
