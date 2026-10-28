#include <stdio.h>
#include "simparameters.h"
#include "sim_run.h"
#include "lab_seeds.h"
#include "part1_appendix_a.h"

static void
write_csv_header(FILE *csv)
{
  fprintf(csv,
	  "experiment,stations,backoff,arrival_rate,arrival_rate_pkt_per_s,seed,"
	  "packet_tx_time_ms,runs_index,arrivals,successes,"
	  "mean_delay,collisions_per_success,throughput,aggregate_load_G\n");
}

static void
write_csv_row(FILE *csv, const Aloha_Run_Config *cfg,
	      const Aloha_Run_Result *result, size_t run_index)
{
  fprintf(csv,
	  "part1,%d,%.0f,%.6f,%.6f,%u,%.3f,%zu,%ld,%ld,%.9f,%.9f,%.9f,%.9f\n",
	  cfg->number_of_stations,
	  cfg->mean_backoff_duration,
	  cfg->packet_arrival_rate,
	  APPENDIX_A_LAMBDA_PACKETS_PER_SEC(cfg->packet_arrival_rate),
	  cfg->random_seed,
	  APPENDIX_A_PACKET_TX_TIME_MS,
	  run_index,
	  result->arrivals,
	  result->successes,
	  result->mean_delay,
	  result->collisions_per_success,
	  result->throughput,
	  result->aggregate_load_G);
}

int
main(void)
{
  FILE *csv;
  size_t i, s;
  size_t run_index = 0;
  Aloha_Run_Config cfg;
  Aloha_Run_Result result;

  csv = fopen("part1_results.csv", "w");
  if(!csv) {
    perror("part1_results.csv");
    return 1;
  }
  write_csv_header(csv);

  cfg.packet_arrival_rate = APPENDIX_A_ARRIVAL_RATE;
  cfg.use_binary_exponential_backoff = 0;
  cfg.persistent_station_id = -1;
  cfg.runlength = SWEEP_RUNLENGTH;
  cfg.print_results = 0;

  for(i = 0; i < APPENDIX_A_NUM_CONFIGS; i++) {
    cfg.number_of_stations = appendix_a_configs[i][0];
    cfg.mean_backoff_duration = (double) appendix_a_configs[i][1];

    for(s = 0; s < APPENDIX_A_NUM_SEEDS; s++) {
      cfg.random_seed = appendix_a_seeds[s];
      aloha_run_simulation(&cfg, &result);
      write_csv_row(csv, &cfg, &result, ++run_index);
      printf("Part1 %zu/%d: N=%d backoff=%d lambda=%.2f seed=%u D=%.3f\n",
	     run_index,
	     APPENDIX_A_NUM_RUNS,
	     cfg.number_of_stations,
	     appendix_a_configs[i][1],
	     cfg.packet_arrival_rate,
	     cfg.random_seed,
	     result.mean_delay);
    }
  }

  fclose(csv);
  printf("Wrote part1_results.csv (%d runs, lambda fixed at %.2f).\n",
	 APPENDIX_A_NUM_RUNS, APPENDIX_A_ARRIVAL_RATE);
  puts("Plots: python3 plot_part1.py");
  return 0;
}
