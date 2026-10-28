#ifndef _PART3_SETTINGS_H_
#define _PART3_SETTINGS_H_

#include "lab_seeds.h"

/*
 * Lab 3 Part 3 (PDF Section 2.3).
 * BEB: uniform on [0, 2^Nc) packet Tx times.
 * Compare BEB vs fixed mean backoff for N=5 and N=10.
 * Runs = 4 seeds x 2 N x 2 modes x 8 lambda = 128.
 */

#define PART3_NUM_SEEDS     LAB_NUM_SEEDS
#define PART3_NUM_CONFIGS   2
#define PART3_NUM_RATES     8
#define PART3_NUM_MODES     2
#define PART3_NUM_RUNS      (PART3_NUM_SEEDS * PART3_NUM_CONFIGS * PART3_NUM_RATES * PART3_NUM_MODES)

#define part3_seeds lab_seeds

static const struct {
  int stations;
  double fixed_backoff;
} part3_configs[PART3_NUM_CONFIGS] = {
  {10, 10.0},
  {5, 5.0}
};

static const double part3_arrival_rates[PART3_NUM_RATES] = {
  0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40
};

#endif /* part3_settings.h */
