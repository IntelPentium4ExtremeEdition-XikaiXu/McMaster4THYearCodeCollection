#include "main.h"
#include "cleanup_memory.h"

static void clean_queue(Fifoqueue_Ptr buffer)
{
  while (fifoqueue_size(buffer) > 0)
    xfree(fifoqueue_get(buffer));
  xfree(buffer);
}

void cleanup_memory(Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);

  if (server_state(data->link) == BUSY)
    xfree(server_get(data->link));
  xfree(data->link);

  clean_queue(data->voice_buffer);
  clean_queue(data->data_buffer);

  simulation_run_free_memory(simulation_run);
}
