# COE4DK4 Lab 2 Part 5 replacement package

This package implements one shared FCFS queue and one output link for periodic
Voice packets and Poisson Data packets.

## Replace these files

- main.c
- main.h
- simparameters.h
- packet_arrival.c
- packet_arrival.h
- packet_transmission.c
- packet_transmission.h
- cleanup_memory.c
- cleanup_memory.h
- output.c
- output.h

Keep the original:

- simlib.c
- simlib.h
- trace.h

The package also includes `plot_part5.py`.

## Install

Back up the existing source directory first, then extract this ZIP into the
Part 5 directory with overwrite enabled.

```bash
unzip -o part5_replacement_files.zip
```

## Compile

```bash
gcc -std=c11 -O2 -Wall -Wextra *.c -o part5 -lm
```

## Run

```bash
./part5
```

The simulator creates `part5_results.csv`.

## Plot

```bash
python3 plot_part5.py
```

This creates `part5_summary.csv` and `part5_delay_vs_data_rate.png`.

## Model assumptions

- Voice packets arrive exactly every 20 ms.
- Voice packet length is 1776 bits.
- The shared link rate is 1 Mbit/s.
- Data arrivals are Poisson.
- Data service time is exponential with a 40 ms mean.
- Voice and Data packets use one strict FCFS queue, with no priority.
- The program scans Data arrival rates from 1 to 22 packets/s.

The theoretical stability boundary under these assumptions is approximately
22.78 Data packets/s. The supplied scan remains below that boundary.

Start with `RUNLENGTH 1000000L`. Increase it only if the lab instructions
require a longer final run.
