#include <stdio.h>
#include "lab_seeds.h"
#include "simparameters.h"
#include "sim_run.h"

static const struct {
  int stations;
  double fixed_backoff;
} part3_configs[] = {
  {10, 10.0},
  {5, 5.0}
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
  size_t i, j, s, mode;
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

  for(i = 0; i < sizeof(part3_configs)/sizeof(part3_configs[0]); i++) {
    cfg.number_of_stations = part3_configs[i].stations;
    cfg.mean_backoff_duration = part3_configs[i].fixed_backoff;

    for(mode = 0; mode < 2; mode++) {
      cfg.use_binary_exponential_backoff = (int) mode;
      mode_name = mode ? "BEB" : "fixed";

      for(j = 0; j < sizeof(arrival_rates)/sizeof(arrival_rates[0]); j++) {
	cfg.packet_arrival_rate = arrival_rates[j];

	for(s = 0; (random_seed = random_seeds[s++]) != 0; ) {
	  cfg.random_seed = random_seed;
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
	  printf("Part3: %s N=%d lambda=%.2f seed=%u D=%.3f S=%.4f\n",
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
  puts("Wrote comparison.csv");
  return 0;
}
