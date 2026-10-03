#include <stdio.h>
#include "main.h"
#include "output.h"

static long int total_processed(Simulation_Run_Data_Ptr data)
{
  return data->number_of_packets_processed[0] +
         data->number_of_packets_processed[1] +
         data->number_of_packets_processed[2];
}

void output_progress_msg_to_screen(Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  long int processed;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->blip_counter++;
  processed = total_processed(data);
  if ((data->blip_counter >= BLIPRATE) || (processed >= RUNLENGTH)) {
    data->blip_counter = 0;
    printf("%3.0f%% Processed packets = %ld\r",
           100.0 * (double)processed / RUNLENGTH, processed);
    fflush(stdout);
  }
}

void output_results(Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  int i;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  printf("\nSeed = %u, p12 = %.2f\n", data->random_seed, data->p12);
  for (i = 0; i < 3; i++) {
    printf("Source %d: arrived=%ld, completed=%ld, mean delay=%.6f ms\n",
           i + 1,
           data->arrival_count[i],
           data->number_of_packets_processed[i],
           1000.0 * data->accumulated_delay[i] /
             data->number_of_packets_processed[i]);
  }
}
