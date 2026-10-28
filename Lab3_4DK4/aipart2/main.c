#include <stdio.h>
#include "simparameters.h"
#include "sim_run.h"
#include "part2_settings.h"

int
main(void)
{
  FILE *csv;
  size_t i, j, s;
  size_t run_index = 0;
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

  for(i = 0; i < PART2_NUM_CONFIGS; i++) {
    cfg.number_of_stations = part2_configs[i][0];
    cfg.mean_backoff_duration = (double) part2_configs[i][1];

    for(j = 0; j < PART2_NUM_RATES; j++) {
      cfg.packet_arrival_rate = part2_arrival_rates[j];

      for(s = 0; s < PART2_NUM_SEEDS; s++) {
	cfg.random_seed = part2_seeds[s];
	aloha_run_simulation(&cfg, &result);
	fprintf(csv, "%d,%d,%.6f,%u,%.9f,%.9f,%.9f,%.9f\n",
		cfg.number_of_stations,
		part2_configs[i][1],
		cfg.packet_arrival_rate,
		cfg.random_seed,
		result.mean_delay,
		result.collisions_per_success,
		result.throughput,
		result.aggregate_load_G);
	printf("Part2 %zu/%d: N=%d backoff=%d lambda=%.2f seed=%u S=%.4f G=%.4f D=%.3f\n",
	       ++run_index,
	       PART2_NUM_RUNS,
	       cfg.number_of_stations,
	       part2_configs[i][1],
	       cfg.packet_arrival_rate,
	       cfg.random_seed,
	       result.throughput,
	       result.aggregate_load_G,
	       result.mean_delay);
      }
    }
  }

  fclose(csv);
  printf("Wrote results.csv (%d runs). Plots: python3 plot_results.py\n", PART2_NUM_RUNS);
  return 0;
}
