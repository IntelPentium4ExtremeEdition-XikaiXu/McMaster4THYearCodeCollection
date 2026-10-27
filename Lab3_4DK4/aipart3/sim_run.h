#ifndef _SIM_RUN_H_
#define _SIM_RUN_H_

#include "main.h"

typedef struct {
  int number_of_stations;
  double packet_arrival_rate;
  double mean_backoff_duration;
  int use_binary_exponential_backoff;
  int persistent_station_id;
  long runlength;
  unsigned random_seed;
  int print_results;
} Aloha_Run_Config;

typedef struct {
  long arrivals;
  long successes;
  long collision_count_sum;
  long transmission_attempts;
  double delay_sum;
  double finish_time;
  double throughput;
  double mean_delay;
  double aggregate_load_G;
  double collisions_per_success;
  /* Filled when persistent_station_id >= 0 in config. */
  int persistent_station_id;
  double persistent_mean_delay;
  double persistent_throughput;
  double other_stations_mean_delay;
  double other_stations_mean_throughput;
} Aloha_Run_Result;

void aloha_run_simulation(const Aloha_Run_Config *cfg, Aloha_Run_Result *result);

#endif /* sim_run.h */
