#include <stdio.h>
#include "main.h"
#include "packet_arrival.h"
#include "cleanup_memory.h"
#include "output.h"

static long int total_processed(const Simulation_Run_Data *data)
{
  return data->voice_processed_count + data->data_processed_count;
}

int main(void)
{
  Simulation_Run_Ptr simulation_run;
  Simulation_Run_Data data;
  FILE *csv_file;

  const double data_arrival_rates[] = {
    1, 3, 5, 7, 9, 11, 13,
    15, 17, 19, 20, 21, 22
  };
  const int number_of_rates =
    (int)(sizeof(data_arrival_rates) / sizeof(data_arrival_rates[0]));

  unsigned random_seeds[] = {RANDOM_SEED_LIST, 0};
  unsigned random_seed;
  int rate_index;
  int seed_index;

  csv_file = fopen("part5_results.csv", "w");
  if (csv_file == NULL) {
    perror("part5_results.csv");
    return 1;
  }

  fprintf(csv_file,
          "data_lambda,seed,voice_completed,data_completed,"
          "voice_delay_ms,data_delay_ms\n");

  for (rate_index = 0; rate_index < number_of_rates; rate_index++) {
    seed_index = 0;

    while ((random_seed = random_seeds[seed_index++]) != 0) {
      simulation_run = simulation_run_new();
      simulation_run_attach_data(simulation_run, &data);

      data.blip_counter = 0;
      data.voice_arrival_count = 0;
      data.data_arrival_count = 0;
      data.voice_processed_count = 0;
      data.data_processed_count = 0;
      data.voice_accumulated_delay = 0.0;
      data.data_accumulated_delay = 0.0;
      data.data_arrival_rate = data_arrival_rates[rate_index];
      data.random_seed = random_seed;

      data.buffer = fifoqueue_new();
      data.link = server_new();

      random_generator_initialize(random_seed);
      schedule_voice_packet_arrival_event(simulation_run, 0.0);
      schedule_data_packet_arrival_event(simulation_run, 0.0);

      while (total_processed(&data) < RUNLENGTH)
        simulation_run_execute_event(simulation_run);

      output_results(simulation_run);

      fprintf(csv_file,
              "%.1f,%u,%ld,%ld,%.8f,%.8f\n",
              data.data_arrival_rate,
              data.random_seed,
              data.voice_processed_count,
              data.data_processed_count,
              1000.0 * data.voice_accumulated_delay /
                data.voice_processed_count,
              1000.0 * data.data_accumulated_delay /
                data.data_processed_count);
      fflush(csv_file);

      cleanup_memory(simulation_run);
    }
  }

  fclose(csv_file);
  printf("\nResults saved to part5_results.csv\n");
  return 0;
}
