#include <stdio.h>
#include "main.h"
#include "output.h"

static long int total_processed(Simulation_Run_Data_Ptr data)
{
  return data->voice_processed_count + data->data_processed_count;
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
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);

  printf("\nSeed = %u, data lambda = %.2f packets/s\n",
         data->random_seed, data->data_arrival_rate);
  printf("Voice: arrived=%ld, completed=%ld, mean delay=%.6f ms\n",
         data->voice_arrival_count,
         data->voice_processed_count,
         1000.0 * data->voice_accumulated_delay /
           data->voice_processed_count);
  printf("Data: arrived=%ld, completed=%ld, mean delay=%.6f ms\n",
         data->data_arrival_count,
         data->data_processed_count,
         1000.0 * data->data_accumulated_delay /
           data->data_processed_count);
}
