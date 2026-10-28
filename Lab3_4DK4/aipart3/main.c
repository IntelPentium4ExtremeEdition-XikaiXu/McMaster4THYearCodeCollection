#include <stdio.h>
#include "simparameters.h"
#include "sim_run.h"
#include "part3_settings.h"

int
main(void)
{
  FILE *csv;
  size_t i, j, s, mode;
  size_t run_index = 0;
  Aloha_Run_Config cfg;
  Aloha_Run_Result result;
  const char *mode_name;

  csv = fopen("comparison.csv", "w");
  if(!csv) {
    perror("comparison.csv");
    return 1;
  }

  fprintf(csv,
	  "mode,stations,fixed_backoff,arrival_rate,seed,mean_delay,"
	  "throughput,aggregate_load_G,collisions_per_success\n");

  cfg.persistent_station_id = -1;
  cfg.runlength = SWEEP_RUNLENGTH;
  cfg.print_results = 0;

  for(i = 0; i < PART3_NUM_CONFIGS; i++) {
    cfg.number_of_stations = part3_configs[i].stations;
    cfg.mean_backoff_duration = part3_configs[i].fixed_backoff;

    for(mode = 0; mode < PART3_NUM_MODES; mode++) {
      cfg.use_binary_exponential_backoff = (int) mode;
      mode_name = mode ? "BEB" : "fixed";

      for(j = 0; j < PART3_NUM_RATES; j++) {
	cfg.packet_arrival_rate = part3_arrival_rates[j];

	for(s = 0; s < PART3_NUM_SEEDS; s++) {
	  cfg.random_seed = part3_seeds[s];
	  aloha_run_simulation(&cfg, &result);
	  fprintf(csv,
		  "%s,%d,%.0f,%.6f,%u,%.9f,%.9f,%.9f,%.9f\n",
		  mode_name,
		  cfg.number_of_stations,
		  part3_configs[i].fixed_backoff,
		  cfg.packet_arrival_rate,
		  cfg.random_seed,
		  result.mean_delay,
		  result.throughput,
		  result.aggregate_load_G,
		  result.collisions_per_success);
	  printf("Part3 %zu/%d: %s N=%d lambda=%.2f seed=%u D=%.3f S=%.4f\n",
		 ++run_index,
		 PART3_NUM_RUNS,
		 mode_name,
		 cfg.number_of_stations,
		 cfg.packet_arrival_rate,
		 cfg.random_seed,
		 result.mean_delay,
		 result.throughput);
	}
      }
    }
  }

  fclose(csv);
  printf("Wrote comparison.csv (%d runs). Plots: python3 plot_comparison.py\n",
	 PART3_NUM_RUNS);
  return 0;
}
