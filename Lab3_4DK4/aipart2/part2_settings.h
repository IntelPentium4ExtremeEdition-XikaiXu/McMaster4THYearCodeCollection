#ifndef _PART2_SETTINGS_H_
#define _PART2_SETTINGS_H_

/*
 * Lab 3 Part 2 (PDF Section 2.2).
 * Same six (N, backoff) pairs as Part 1, but lambda is swept so S–lambda,
 * D–S, and S–G can be plotted. Fixed backoff, no BEB, no persistent station.
 *
 * Runs = 4 seeds x 6 configs x 8 arrival rates = 192.
 */

#include "lab_seeds.h"

#define PART2_NUM_SEEDS     LAB_NUM_SEEDS
#define PART2_NUM_CONFIGS   6
#define PART2_NUM_RATES     8
#define PART2_NUM_RUNS      (PART2_NUM_SEEDS * PART2_NUM_CONFIGS * PART2_NUM_RATES)

#define part2_seeds lab_seeds

static const int part2_configs[PART2_NUM_CONFIGS][2] = {
  {10, 5}, {10, 10}, {10, 20},
  {5, 3}, {5, 5}, {5, 7}
};

static const double part2_arrival_rates[PART2_NUM_RATES] = {
  0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40
};

#endif /* part2_settings.h */
