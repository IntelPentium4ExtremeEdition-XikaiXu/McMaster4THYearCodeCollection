#ifndef _PART4_SETTINGS_H_
#define _PART4_SETTINGS_H_

#include "lab_seeds.h"

/*
 * Lab 3 Part 4 (PDF Section 2.4).
 * Station 0 retries immediately after a collision (no backoff).
 * Other stations use BEB [0, 2^Nc). Compare delay and throughput
 * of station 0 vs the average of the others; also vs all-BEB baseline.
 *
 * Runs = 4 seeds x 8 lambda x 2 modes = 64.
 */

#define PART4_NUM_SEEDS   LAB_NUM_SEEDS
#define PART4_NUM_RATES   8
#define PART4_NUM_MODES   2
#define PART4_NUM_RUNS    (PART4_NUM_SEEDS * PART4_NUM_RATES * PART4_NUM_MODES)

#define part4_seeds lab_seeds

static const double part4_arrival_rates[PART4_NUM_RATES] = {
  0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40
};

#endif /* part4_settings.h */
