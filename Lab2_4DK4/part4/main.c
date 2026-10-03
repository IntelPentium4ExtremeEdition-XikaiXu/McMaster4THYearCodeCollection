#include <stdio.h>
#include "main.h"
#include "packet_arrival.h"
#include "cleanup_memory.h"
#include "output.h"

static long int total_processed(const Simulation_Run_Data *data)
{
  return data->number_of_packets_processed[0] +
         data->number_of_packets_processed[1] +
         data->number_of_packets_processed[2];
}

int main(void)
{
  Simulation_Run_Ptr simulation_run;
  Simulation_Run_Data data;
  FILE *csv_file;
  const double p12_values[] = {
    0.0, 0.1, 0.2, 0.3, 0.4, 0.5,
    0.6, 0.7, 0.8, 0.9, 1.0
  };
  const int number_of_p12_values =
    (int)(sizeof(p12_values) / sizeof(p12_values[0]));
  unsigned random_seeds[] = {RANDOM_SEED_LIST, 0};
  unsigned random_seed;
  int p_index;
  int seed_index;
  int i;

  csv_file = fopen("part4_results.csv", "w");
  if (csv_file == NULL) {
    perror("part4_results.csv");
    return 1;
  }
  fprintf(csv_file,
          "p12,seed,source1_completed,source2_completed,source3_completed,"
          "source1_delay_ms,source2_delay_ms,source3_delay_ms\n");

  for (p_index = 0; p_index < number_of_p12_values; p_index++) {
    seed_index = 0;
    while ((random_seed = random_seeds[seed_index++]) != 0) {
      simulation_run = simulation_run_new();
      simulation_run_attach_data(simulation_run, &data);

      data.blip_counter = 0;
      data.p12 = p12_values[p_index];
      data.random_seed = random_seed;
      for (i = 0; i < 3; i++) {
        data.arrival_count[i] = 0;
        data.number_of_packets_processed[i] = 0;
        data.accumulated_delay[i] = 0.0;
      }

      data.buffer1 = fifoqueue_new();
      data.buffer2 = fifoqueue_new();
      data.buffer3 = fifoqueue_new();
      data.link1 = server_new();
      data.link2 = server_new();
      data.link3 = server_new();

      random_generator_initialize(random_seed);
      schedule_packet_arrival_1_event(simulation_run, 0.0);
      schedule_packet_arrival_2_event(simulation_run, 0.0);
      schedule_packet_arrival_3_event(simulation_run, 0.0);

      while (total_processed(&data) < RUNLENGTH)
        simulation_run_execute_event(simulation_run);

      output_results(simulation_run);
      fprintf(csv_file,
              "%.1f,%u,%ld,%ld,%ld,%.8f,%.8f,%.8f\n",
              data.p12,
              data.random_seed,
              data.number_of_packets_processed[0],
              data.number_of_packets_processed[1],
              data.number_of_packets_processed[2],
              1000.0 * data.accumulated_delay[0] /
                data.number_of_packets_processed[0],
              1000.0 * data.accumulated_delay[1] /
                data.number_of_packets_processed[1],
              1000.0 * data.accumulated_delay[2] /
                data.number_of_packets_processed[2]);
      fflush(csv_file);
      cleanup_memory(simulation_run);
    }
  }

  fclose(csv_file);
  printf("\nResults saved to part4_results.csv\n");
  return 0;
}
