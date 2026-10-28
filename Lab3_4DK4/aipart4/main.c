#include <stdio.h>
#include "simparameters.h"
#include "sim_run.h"
#include "part4_settings.h"

int
main(void)
{
  FILE *csv;
  size_t j, r, s;
  size_t run_index = 0;
  Aloha_Run_Config cfg;
  Aloha_Run_Result result;
  const char *mode_label;

  csv = fopen("part4_results.csv", "w");
  if(!csv) {
    perror("part4_results.csv");
    return 1;
  }

  fprintf(csv,
	  "mode,stations,persistent_station_id,arrival_rate,seed,runlength,"
	  "system_mean_delay,system_throughput,aggregate_load_G,"
	  "persistent_mean_delay,persistent_throughput,"
	  "other_mean_delay,other_mean_throughput,"
	  "delay_ratio_persist_over_other,throughput_ratio_persist_over_other\n");

  cfg.number_of_stations = NUMBER_OF_STATIONS;
  cfg.mean_backoff_duration = MEAN_BACKOFF_DURATION;
  cfg.use_binary_exponential_backoff = 1;
  cfg.runlength = SWEEP_RUNLENGTH;
  cfg.print_results = 0;

  for(r = 0; r < PART4_NUM_RATES; r++) {
    cfg.packet_arrival_rate = part4_arrival_rates[r];

    for(s = 0; s < PART4_NUM_SEEDS; s++) {
      cfg.random_seed = part4_seeds[s];

      for(j = 0; j < PART4_NUM_MODES; j++) {
	if(j == 0) {
	  cfg.persistent_station_id = PERSISTENT_STATION_ID;
	  mode_label = "persistent";
	} else {
	  cfg.persistent_station_id = -1;
	  mode_label = "beb_baseline";
	}

	aloha_run_simulation(&cfg, &result);

	fprintf(csv,
		"%s,%d,%d,%.6f,%u,%ld,%.9f,%.9f,%.9f,",
		mode_label,
		cfg.number_of_stations,
		cfg.persistent_station_id,
		cfg.packet_arrival_rate,
		cfg.random_seed,
		cfg.runlength,
		result.mean_delay,
		result.throughput,
		result.aggregate_load_G);

	if(cfg.persistent_station_id >= 0) {
	  double delay_ratio = 0.0;
	  double throughput_ratio = 0.0;

	  if(result.other_stations_mean_delay > 0.0) {
	    delay_ratio =
	      result.persistent_mean_delay / result.other_stations_mean_delay;
	  }
	  if(result.other_stations_mean_throughput > 0.0) {
	    throughput_ratio =
	      result.persistent_throughput /
	      result.other_stations_mean_throughput;
	  }

	  fprintf(csv,
		  "%.9f,%.9f,%.9f,%.9f,%.9f,%.9f\n",
		  result.persistent_mean_delay,
		  result.persistent_throughput,
		  result.other_stations_mean_delay,
		  result.other_stations_mean_throughput,
		  delay_ratio,
		  throughput_ratio);
	} else {
	  fprintf(csv, ",,,,,\n");
	}

	printf("Part4 %zu/%d: %s lambda=%.2f seed=%u D_sys=%.3f S=%.4f",
	       ++run_index,
	       PART4_NUM_RUNS,
	       mode_label,
	       cfg.packet_arrival_rate,
	       cfg.random_seed,
	       result.mean_delay,
	       result.throughput);
	if(cfg.persistent_station_id >= 0) {
	  printf(" D_persist=%.3f D_other=%.3f",
		 result.persistent_mean_delay,
		 result.other_stations_mean_delay);
	}
	printf("\n");
      }
    }
  }

  fclose(csv);
  printf("Wrote part4_results.csv (%d runs). Plots: python3 plot_part4.py\n",
	 PART4_NUM_RUNS);
  return 0;
}
