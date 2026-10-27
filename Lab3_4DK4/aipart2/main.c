#include <stdio.h>
#include "lab_seeds.h"
#include "simparameters.h"
#include "sim_run.h"

static const int station_backoff_configs[][2] = {
  {10, 5}, {10, 10}, {10, 20},
  {5, 3}, {5, 5}, {5, 7}
};

static const double arrival_rates[] = {
  0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40
};

int
main(void)
{
  unsigned random_seed;
  unsigned random_seeds[] = {RANDOM_SEED_LIST, 0};
  FILE *csv;
  size_t i, j, s;
  Aloha_Run_Config cfg;
  Aloha_Run_Result result;

  csv = fopen("results.csv", "w");
  if(!csv) {
    perror("results.csv");
    return 1;
  }

  fprintf(csv,
	  "stations,backoff,arrival_rate,seed,mean_delay,collisions_per_success,"
	  "throughput,aggregate_load_G\n");

  cfg.use_binary_exponential_backoff = 0;
  cfg.persistent_station_id = -1;
  cfg.runlength = SWEEP_RUNLENGTH;
  cfg.print_results = 0;

  for(i = 0; i < sizeof(station_backoff_configs)/sizeof(station_backoff_configs[0]); i++) {
    cfg.number_of_stations = station_backoff_configs[i][0];
    cfg.mean_backoff_duration = (double) station_backoff_configs[i][1];

    for(j = 0; j < sizeof(arrival_rates)/sizeof(arrival_rates[0]); j++) {
      cfg.packet_arrival_rate = arrival_rates[j];

      for(s = 0; (random_seed = random_seeds[s++]) != 0; ) {
	cfg.random_seed = random_seed;
	aloha_run_simulation(&cfg, &result);
	fprintf(csv, "%d,%d,%.6f,%u,%.9f,%.9f,%.9f,%.9f\n",
		cfg.number_of_stations,
		station_backoff_configs[i][1],
		cfg.packet_arrival_rate,
		cfg.random_seed,
		result.mean_delay,
		result.collisions_per_success,
		result.throughput,
		result.aggregate_load_G);
	printf("Part2: N=%d backoff=%d lambda=%.2f seed=%u S=%.4f G=%.4f\n",
	       cfg.number_of_stations,
	       station_backoff_configs[i][1],
	       cfg.packet_arrival_rate,
	       cfg.random_seed,
	       result.throughput,
	       result.aggregate_load_G);
      }
    }
  }

  fclose(csv);
  puts("Wrote results.csv");
  return 0;
}
