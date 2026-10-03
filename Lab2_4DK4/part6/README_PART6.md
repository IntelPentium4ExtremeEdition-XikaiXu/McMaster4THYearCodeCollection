# COE4DK4 Lab 2 Part 6 replacement package

Part 6 uses two waiting queues and one output link:

- Voice queue: high priority
- Data queue: low priority
- Non-preemptive service

A Data packet already in transmission is never interrupted. Whenever the link
finishes the current packet, the simulator checks the Voice queue first. The
Data queue is used only when the Voice queue is empty.

## Recommended setup

Copy Part 5 to a new Part 6 directory, then extract this ZIP with overwrite:

```bash
cd ~/Development/McMaster4THYearMatlabs/Lab2_4DK4
cp -r part5 part6
cd part6
unzip -o part6_replacement_files.zip
```

Keep the existing `simlib.c`, `simlib.h`, and `trace.h`.

## Compile and run

```bash
gcc -std=c11 -O2 -Wall -Wextra *.c -o part6 -lm
./part6
```

The result file is `part6_results.csv`.

## Plot Part 6

```bash
python3 plot_part6.py
```

## Compare Part 5 and Part 6

The comparison script assumes this directory structure:

```text
Lab2_4DK4/
  part5/part5_results.csv
  part6/part6_results.csv
```

Run from the Part 6 directory:

```bash
python3 compare_part5_part6.py
```

Expected behavior:

- Voice delay is much lower than in Part 5.
- Data delay is higher than in Part 5.
- Voice delay is not zero because the priority is non-preemptive.
- Near the stability boundary, Data delay can become very large.
